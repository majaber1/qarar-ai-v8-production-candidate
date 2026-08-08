from app.core.config import settings
CONNECTORS=[
 {'id':'m365','name':'Microsoft 365','channels':['Outlook','Teams','SharePoint','OneDrive','Calendar'],'kind':'oauth','configured':lambda:bool(settings.m365_client_id and settings.m365_tenant_id),'status':'ready_to_configure'},
 {'id':'google','name':'Google Workspace','channels':['Gmail','Drive','Calendar'],'kind':'oauth','configured':lambda:bool(settings.google_client_id),'status':'ready_to_configure'},
 {'id':'github','name':'GitHub','channels':['Repos','Issues','PRs','Actions'],'kind':'mcp_or_token','configured':lambda:bool(settings.github_token),'status':'ready_to_configure'},
 {'id':'imap','name':'Generic IMAP','channels':['Email'],'kind':'native','configured':lambda:bool(settings.imap_enabled and settings.imap_host and settings.imap_username),'status':'active_adapter'},
 {'id':'mcp','name':'Any Remote MCP','channels':['Tools','Resources'],'kind':'mcp','configured':lambda:True,'status':'active_gateway'},
 {'id':'n8n','name':'n8n','channels':['Automation','Webhooks'],'kind':'automation','configured':lambda:bool(settings.automation_enabled),'status':'active_adapter'},
]
def catalog():return [{**{k:v for k,v in x.items() if k!='configured'},'configured':x['configured']()} for x in CONNECTORS]
