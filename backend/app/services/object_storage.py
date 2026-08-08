from __future__ import annotations
from pathlib import Path
import os, uuid
from app.core.config import settings

class LocalObjectStorage:
    def __init__(self): self.root=Path(settings.object_storage_local_path)
    def _path(self,key:str)->Path:
        root=self.root.resolve();target=(root/key).resolve()
        if root not in target.parents:raise ValueError('Invalid object key')
        return target
    def put(self,name:str,data:bytes)->str:
        self.root.mkdir(parents=True,exist_ok=True)
        safe=''.join(c if c.isalnum() or c in '._-' else '_' for c in name)[:160]
        key=f"{uuid.uuid4().hex}_{safe}"
        self._path(key).write_bytes(data); return key
    def get(self,key:str)->bytes: return self._path(key).read_bytes()
    def delete(self,key:str):
        p=self._path(key)
        if p.exists(): p.unlink()

class S3ObjectStorage:
    def __init__(self):
        import boto3
        self.client=boto3.client('s3',endpoint_url=settings.s3_endpoint_url or None,
            aws_access_key_id=settings.s3_access_key or None,aws_secret_access_key=settings.s3_secret_key or None,
            region_name=settings.s3_region)
        self.bucket=settings.s3_bucket
        try:self.client.head_bucket(Bucket=self.bucket)
        except Exception:
            try:self.client.create_bucket(Bucket=self.bucket)
            except Exception:pass
    def put(self,name:str,data:bytes)->str:
        safe=''.join(c if c.isalnum() or c in '._-' else '_' for c in Path(name).name)[:160]
        key=f"uploads/{uuid.uuid4().hex}/{safe}"
        self.client.put_object(Bucket=self.bucket,Key=key,Body=data); return key
    def get(self,key:str)->bytes:return self.client.get_object(Bucket=self.bucket,Key=key)['Body'].read()
    def delete(self,key:str):self.client.delete_object(Bucket=self.bucket,Key=key)

def storage():
    return S3ObjectStorage() if settings.object_storage_provider.lower() in {'s3','minio'} else LocalObjectStorage()
