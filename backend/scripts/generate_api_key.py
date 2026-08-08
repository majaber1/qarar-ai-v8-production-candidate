import argparse,json,secrets
p=argparse.ArgumentParser();p.add_argument('--tenant',required=True);p.add_argument('--subject',required=True);p.add_argument('--roles',default='project_manager');a=p.parse_args()
key='qk_'+secrets.token_urlsafe(32)
roles=[x.strip() for x in a.roles.split(',') if x.strip()]
print('KEY='+key)
print('REGISTRY_ENTRY='+json.dumps({key:{'tenant_id':a.tenant,'subject':a.subject,'roles':roles}},separators=(',',':')))
