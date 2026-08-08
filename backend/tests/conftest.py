import os
from pathlib import Path

TEST_DB=Path('./test_qarar_v51.db')
if TEST_DB.exists():TEST_DB.unlink()
os.environ['DATABASE_URL']=f'sqlite:///{TEST_DB}'
os.environ['AI_ENABLED']='false'
os.environ['ENVIRONMENT']='test'
os.environ['AUTOMATION_ENABLED']='false'
os.environ['QARAR_API_KEYS_JSON']='{"key-a":{"tenant_id":"tenant-a","subject":"admin-a","roles":["admin","executive","project_manager","developer"]},"key-b":{"tenant_id":"tenant-b","subject":"admin-b","roles":["admin","executive","project_manager","developer"]},"reader-a":{"tenant_id":"tenant-a","subject":"reader-a","roles":["executive"]}}'
