from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    environment:str='development'
    database_url:str='sqlite:///./qarar.db'
    cors_origins:str='http://localhost:3000'

    # Authentication / tenant isolation. Secure-by-default: API calls require a key.
    auth_required:bool=True
    qarar_api_keys_json:str='{}'
    mcp_tenant_id:str='default'

    # OIDC / SSO (reference scaffold — production requires a real tenant/issuer configuration).
    oidc_enabled:bool=False
    oidc_issuer:str|None=None
    oidc_client_id:str|None=None
    oidc_client_secret:str|None=None
    oidc_audience:str|None=None
    oidc_jwks_url:str|None=None
    oidc_role_claim:str='roles'
    oidc_tenant_claim:str='tenant_id'

    ai_enabled:bool=False
    ai_provider:str='mock'
    ai_model:str='gpt-5.6-luna'
    ai_api_key:str|None=None
    embedding_model:str='text-embedding-3-small'
    embedding_dimensions:int=1536
    response_language:str='ar'
    ai_timeout_seconds:float=90
    ai_max_retries:int=2
    estimated_input_usd_per_million:float=1.25
    estimated_output_usd_per_million:float=10.0
    max_file_mb:int=100
    ingestion_mode:str='sync'
    object_storage_provider:str='local'
    object_storage_local_path:str='./data/objects'
    s3_endpoint_url:str|None=None
    s3_bucket:str='qarar'
    s3_access_key:str|None=None
    s3_secret_key:str|None=None
    s3_region:str='us-east-1'
    chunk_chars:int=2200
    chunk_overlap:int=300
    hybrid_vector_weight:float=.55
    hybrid_lexical_weight:float=.30
    hybrid_trust_weight:float=.15
    research_enabled:bool=False
    research_mode_default:str='official_plus_organization'
    official_domains:str='nca.gov.sa,dga.gov.sa,sdaia.gov.sa,cst.gov.sa'
    public_web_enabled:bool=False
    imap_enabled:bool=False
    imap_host:str|None=None
    imap_port:int=993
    imap_username:str|None=None
    imap_password:str|None=None
    imap_mailbox:str='INBOX'
    imap_use_ssl:bool=True
    m365_client_id:str|None=None
    m365_tenant_id:str|None=None
    m365_client_secret:str|None=None
    google_client_id:str|None=None
    google_client_secret:str|None=None
    github_token:str|None=None
    api_public_base_url:str='http://localhost:8000'
    mcp_public_base_url:str='http://localhost:8001'
    mcp_allowed_hosts:str='localhost:*,127.0.0.1:*'
    mcp_allowed_origins:str='http://localhost:3000'
    mcp_api_key:str|None=None
    mcp_servers_file:str='./config/mcp_servers.json'
    mcp_gateway_timeout_seconds:float=20.0
    automation_enabled:bool=False
    n8n_webhook_base_url:str='http://localhost:5678/webhook'
    n8n_api_key:str|None=None
    automation_require_approval:bool=True
    automation_dry_run:bool=True
    automation_callback_secret:str|None=None
    automation_callback_max_skew_seconds:int=300
    automation_allowed_hosts:str='localhost,127.0.0.1,n8n'
    database_pool_size:int=10
    database_max_overflow:int=20

    # Malware scanning (ClamAV/clamd). If disabled, uploads are marked 'scan_skipped' explicitly
    # rather than silently presented as scanned/trusted.
    malware_scan_enabled:bool=False
    clamav_host:str='localhost'
    clamav_port:int=3310
    clamav_timeout_seconds:float=15.0

    # Rate limiting / denial-of-wallet controls. In-process sliding window; swap for a shared
    # backend (Redis) before multi-process/production deployment.
    rate_limit_enabled:bool=True
    rate_limit_requests_per_minute_user:int=120
    rate_limit_requests_per_minute_tenant:int=600
    rate_limit_ai_requests_per_minute_user:int=20

    # Cost governance. Budgets are enforced per tenant per UTC day unless a CostBudget row overrides it.
    default_tenant_daily_budget_usd:float=25.0
    default_case_run_budget_usd:float=2.0

    model_config=SettingsConfigDict(env_file='.env',env_file_encoding='utf-8',extra='ignore')

    @property
    def cors_list(self): return [x.strip() for x in self.cors_origins.split(',') if x.strip()]
    @property
    def official_domain_list(self): return [x.strip() for x in self.official_domains.split(',') if x.strip()]
    @property
    def mcp_host_list(self): return [x.strip() for x in self.mcp_allowed_hosts.split(',') if x.strip()]
    @property
    def mcp_origin_list(self): return [x.strip() for x in self.mcp_allowed_origins.split(',') if x.strip()]
    @property
    def automation_allowed_host_list(self): return [x.strip().lower() for x in self.automation_allowed_hosts.split(',') if x.strip()]
    @property
    def is_postgres(self): return self.database_url.startswith('postgresql')

settings=Settings()
