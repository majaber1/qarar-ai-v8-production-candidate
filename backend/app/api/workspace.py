from __future__ import annotations
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import os
import secrets
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.audit import record_audit
from app.core.auth import Principal, require_principal, require_roles
from app.core.database import get_db
from app.models.workspace import AccessRequest, Project, UserSession, WorkspaceUser
from app.models.case import DecisionCase
from app.models.fabric import KnowledgeSource

router = APIRouter(tags=['workspace'])
ROLES = {'project_manager', 'executive', 'analyst', 'developer'}


def _password_hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 310_000)
    return f'pbkdf2_sha256$310000${salt.hex()}${digest.hex()}'


def _password_ok(password: str, encoded: str) -> bool:
    try:
        _, rounds, salt, digest = encoded.split('$', 3)
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), int(rounds)).hex()
        return hmac.compare_digest(actual, digest)
    except Exception:
        return False


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    email: str = Field(min_length=5, max_length=320, pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    organization: str = Field(min_length=2, max_length=250)
    workspace_code: str = Field(min_length=2, max_length=80, pattern=r'^[a-zA-Z0-9_-]+$')
    password: str = Field(min_length=12, max_length=200)
    requested_role: str = 'project_manager'


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320, pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    workspace_code: str
    password: str

class LogoutRequest(BaseModel):
    token: str = Field(min_length=20, max_length=500)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=3, max_length=250)
    objective: str = Field(min_length=10, max_length=4000)
    owner: str = Field(min_length=2, max_length=200)

class ProjectUpdate(BaseModel):
    name:str|None=Field(default=None,min_length=3,max_length=250)
    objective:str|None=Field(default=None,min_length=10,max_length=4000)
    owner:str|None=Field(default=None,min_length=2,max_length=200)
    status:str|None=None

class ProfileUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=12, max_length=200)


def _principal_user(db: Session, principal: Principal) -> WorkspaceUser:
    if principal.auth_type != 'session' or not principal.subject.startswith('user:'):
        raise HTTPException(403, 'Profile management requires a password-authenticated user session')
    user = db.get(WorkspaceUser, int(principal.subject.split(':', 1)[1]))
    if not user or user.tenant_id != principal.tenant_id:
        raise HTTPException(404, 'User not found')
    return user


@router.post('/auth/register', status_code=202)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    role = req.requested_role if req.requested_role in ROLES else 'project_manager'
    email = str(req.email).strip().lower()
    tenant_id = req.workspace_code.strip().lower()
    if db.scalar(select(WorkspaceUser).where(WorkspaceUser.tenant_id == tenant_id, WorkspaceUser.email == email)):
        # Do not disclose whether an email already belongs to a workspace.
        return {'status': 'pending', 'message': 'If eligible, the account request will be reviewed by an administrator'}
    user = WorkspaceUser(tenant_id=tenant_id, email=email, full_name=req.full_name.strip(),
                         organization=req.organization.strip(), password_hash=_password_hash(req.password),
                         role=role, active=False)
    db.add(user); db.flush()
    access = AccessRequest(tenant_id=tenant_id, user_id=user.id, requested_role=role)
    db.add(access); db.commit(); db.refresh(access)
    record_audit(tenant_id, email, 'access_requested', auth_type='registration',
                 resource_type='access_request', resource_id=access.id, metadata={'requested_role': role})
    return {'id': access.id, 'status': 'pending', 'message': 'Account request submitted for administrator approval'}


@router.post('/auth/login')
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(WorkspaceUser).where(
        WorkspaceUser.tenant_id == req.workspace_code.strip().lower(),
        WorkspaceUser.email == str(req.email).strip().lower()))
    if not user or not _password_ok(req.password, user.password_hash):
        raise HTTPException(401, 'Invalid credentials')
    if not user.active:
        raise HTTPException(403, 'Account is awaiting administrator approval')
    raw_token = secrets.token_urlsafe(48)
    session = UserSession(user_id=user.id, token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
                          expires_at=datetime.now(timezone.utc) + timedelta(hours=8))
    db.add(session); db.commit()
    record_audit(user.tenant_id, user.email, 'user_login', auth_type='password', resource_type='user', resource_id=user.id)
    return {'token': raw_token, 'expires_in': 28800, 'identity': {'subject': f'user:{user.id}', 'tenant_id': user.tenant_id,
            'roles': [user.role], 'display_name': user.full_name, 'email': user.email, 'auth_type': 'session'}}


@router.post('/auth/logout')
def logout(req: LogoutRequest, db: Session = Depends(get_db)):
    session = db.scalar(select(UserSession).where(UserSession.token_hash == hashlib.sha256(req.token.encode()).hexdigest()))
    if session:
        session.revoked = True; db.commit()
    return {'status': 'ok'}


@router.get('/profile')
def profile(db: Session = Depends(get_db), principal: Principal = Depends(require_principal)):
    user = _principal_user(db, principal)
    return {'id': user.id, 'tenant_id': user.tenant_id, 'email': user.email, 'full_name': user.full_name,
            'organization': user.organization, 'role': user.role, 'active': user.active}


@router.patch('/profile')
def update_profile(req: ProfileUpdate, db: Session = Depends(get_db), principal: Principal = Depends(require_principal)):
    user = _principal_user(db, principal); user.full_name = req.full_name.strip(); db.commit(); db.refresh(user)
    record_audit(user.tenant_id, user.email, 'profile_updated', auth_type='session', resource_type='user', resource_id=user.id)
    return {'id': user.id, 'email': user.email, 'full_name': user.full_name, 'organization': user.organization, 'role': user.role}


@router.post('/profile/password')
def change_password(req: PasswordChange, db: Session = Depends(get_db), principal: Principal = Depends(require_principal)):
    user = _principal_user(db, principal)
    if not _password_ok(req.current_password, user.password_hash): raise HTTPException(401, 'Current password is incorrect')
    if hmac.compare_digest(req.current_password, req.new_password): raise HTTPException(422, 'New password must be different')
    user.password_hash = _password_hash(req.new_password)
    for session in db.scalars(select(UserSession).where(UserSession.user_id == user.id)).all(): session.revoked = True
    db.commit()
    record_audit(user.tenant_id, user.email, 'password_changed', auth_type='session', resource_type='user', resource_id=user.id)
    return {'status': 'ok', 'sessions_revoked': True}


@router.get('/access-requests')
def access_requests(db: Session = Depends(get_db), principal: Principal = Depends(require_roles('admin'))):
    q = select(AccessRequest, WorkspaceUser).join(WorkspaceUser, WorkspaceUser.id == AccessRequest.user_id).where(
        AccessRequest.tenant_id == principal.tenant_id).order_by(AccessRequest.created_at.desc())
    return [{'id': a.id, 'status': a.status, 'requested_role': a.requested_role, 'created_at': a.created_at,
             'user': {'id': u.id, 'email': u.email, 'full_name': u.full_name, 'organization': u.organization}} for a, u in db.execute(q).all()]


@router.post('/access-requests/{request_id}/approve')
def approve_access(request_id: int, db: Session = Depends(get_db), principal: Principal = Depends(require_roles('admin'))):
    access = db.scalar(select(AccessRequest).where(AccessRequest.id == request_id, AccessRequest.tenant_id == principal.tenant_id))
    if not access: raise HTTPException(404, 'Access request not found')
    user = db.get(WorkspaceUser, access.user_id)
    if not user: raise HTTPException(404, 'User not found')
    now = datetime.now(timezone.utc)
    user.active = True; user.role = access.requested_role; user.approved_at = now
    access.status = 'approved'; access.reviewed_by = principal.subject; access.reviewed_at = now
    db.commit()
    record_audit(principal.tenant_id, principal.subject, 'access_approved', auth_type=principal.auth_type,
                 resource_type='access_request', resource_id=access.id, metadata={'user_id': user.id, 'role': user.role})
    return {'id': access.id, 'status': access.status}


@router.post('/projects', status_code=201)
def create_project(req: ProjectCreate, db: Session = Depends(get_db), principal: Principal = Depends(require_roles('project_manager','executive'))):
    project = Project(tenant_id=principal.tenant_id, name=req.name.strip(), objective=req.objective.strip(),
                      owner=req.owner.strip(), created_by=principal.subject)
    db.add(project); db.commit(); db.refresh(project)
    record_audit(principal.tenant_id, principal.subject, 'project_created', auth_type=principal.auth_type,
                 resource_type='project', resource_id=project.id, metadata={'name': project.name})
    return project


@router.get('/projects')
def list_projects(db: Session = Depends(get_db), principal: Principal = Depends(require_principal)):
    return list(db.scalars(select(Project).where(Project.tenant_id == principal.tenant_id).order_by(Project.created_at.desc())).all())


@router.get('/projects/{project_id}')
def get_project(project_id: int, db: Session = Depends(get_db), principal: Principal = Depends(require_principal)):
    project = db.scalar(select(Project).where(Project.id == project_id, Project.tenant_id == principal.tenant_id))
    if not project: raise HTTPException(404, 'Project not found')
    cases=list(db.scalars(select(DecisionCase).where(DecisionCase.project_id==project_id,DecisionCase.tenant_id==principal.tenant_id)).all())
    evidence=list(db.scalars(select(KnowledgeSource).where(KnowledgeSource.project_id==project_id,KnowledgeSource.tenant_id==principal.tenant_id,KnowledgeSource.deleted_at.is_(None))).all())
    return {'id':project.id,'name':project.name,'objective':project.objective,'owner':project.owner,'status':project.status,'created_at':project.created_at,'updated_at':project.updated_at,'summary':{'cases':len(cases),'approved_cases':sum(x.status=='approved' for x in cases),'open_cases':sum(x.status not in {'approved','rejected','archived'} for x in cases),'evidence':len(evidence)},'cases':[{'id':x.id,'title':x.title,'status':x.status} for x in cases],'evidence':[{'id':x.id,'title':x.title,'status':x.status,'version':x.version} for x in evidence]}

@router.patch('/projects/{project_id}')
def update_project(project_id:int,req:ProjectUpdate,db:Session=Depends(get_db),principal:Principal=Depends(require_roles('project_manager','executive'))):
    project=db.scalar(select(Project).where(Project.id==project_id,Project.tenant_id==principal.tenant_id))
    if not project:raise HTTPException(404,'Project not found')
    values=req.model_dump(exclude_unset=True)
    if values.get('status') not in {None,'active','on_hold','archived'}:raise HTTPException(422,'Invalid project status')
    for key,value in values.items():setattr(project,key,value.strip() if isinstance(value,str) else value)
    db.commit();db.refresh(project)
    record_audit(principal.tenant_id,principal.subject,'project_updated',auth_type=principal.auth_type,resource_type='project',resource_id=project.id,metadata={'fields':sorted(values)})
    return project
