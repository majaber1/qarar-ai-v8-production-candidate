from app.services.connectors import catalog
from app.services.mcp_gateway import server_catalog

def test_connector_catalog_has_mcp_and_n8n():
    ids={x['id'] for x in catalog()};assert {'mcp','n8n','github','m365'}<=ids
def test_mcp_config_loads():assert isinstance(server_catalog(),list)
