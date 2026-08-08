"""Regression test for the V5.1 MCP gateway defect: streamable_http_client() does not accept a
`headers=` kwarg in the installed SDK. This test starts a real Qarar MCP server process, points
the real Qarar MCP gateway at it (through app/services/mcp_gateway.py, not a re-implementation),
and proves list_tools()/call_tool() succeed end-to-end — and that an anonymous connection fails.
If this regresses, `pytest` fails here instead of only being caught by manual review.
"""
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def _wait_for_port(port: int, timeout: float = 20.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            try:
                s.connect(('127.0.0.1', port))
                return
            except OSError:
                time.sleep(0.3)
    raise TimeoutError(f'Nothing listening on 127.0.0.1:{port} after {timeout}s')


@pytest.fixture(scope='module')
def live_mcp_server():
    port = _free_port()
    env = {
        **os.environ,
        'DATABASE_URL': f"sqlite:///{BACKEND_DIR / 'test_mcp_gateway_integration.db'}",
        'ENVIRONMENT': 'test',
        'AI_ENABLED': 'false',
        'QARAR_API_KEYS_JSON': json.dumps({
            'gw-integration-key': {'tenant_id': 'gw-tenant', 'subject': 'gw-admin',
                                    'roles': ['admin', 'executive', 'project_manager', 'developer']},
        }),
        'MCP_ALLOWED_HOSTS': '127.0.0.1:*,localhost:*',
        'MCP_ALLOWED_ORIGINS': 'http://localhost:3000',
        'PYTHONPATH': str(BACKEND_DIR),
    }
    db_path = BACKEND_DIR / 'test_mcp_gateway_integration.db'
    if db_path.exists():
        db_path.unlink()
    proc = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'app.mcp_server:app', '--host', '127.0.0.1', '--port', str(port)],
        cwd=str(BACKEND_DIR), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    try:
        _wait_for_port(port)
        time.sleep(0.5)
        yield port
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        if db_path.exists():
            db_path.unlink()


def _configure_gateway(tmp_path, port, with_auth=True):
    servers_file = tmp_path / 'mcp_servers.json'
    servers = {'servers': [{
        'id': 'live-test-server', 'name': 'Live Integration Test Server',
        'url': f'http://127.0.0.1:{port}/mcp', 'enabled': True,
        'auth': {'type': 'bearer', 'env': 'GATEWAY_TEST_TOKEN'} if with_auth else {},
    }]}
    servers_file.write_text(json.dumps(servers), encoding='utf-8')
    return servers_file


def test_gateway_unauthorized_connection_fails(live_mcp_server, tmp_path, monkeypatch):
    from app.core.config import settings
    servers_file = _configure_gateway(tmp_path, live_mcp_server, with_auth=False)
    monkeypatch.setattr(settings, 'mcp_servers_file', str(servers_file))
    monkeypatch.delenv('GATEWAY_TEST_TOKEN', raising=False)

    from app.services import mcp_gateway
    with pytest.raises(Exception):
        mcp_gateway.list_tools('live-test-server', tenant_id='gw-tenant')


def test_gateway_authenticated_list_tools_and_call_health(live_mcp_server, tmp_path, monkeypatch):
    from app.core.config import settings
    servers_file = _configure_gateway(tmp_path, live_mcp_server, with_auth=True)
    monkeypatch.setattr(settings, 'mcp_servers_file', str(servers_file))
    monkeypatch.setenv('GATEWAY_TEST_TOKEN', 'gw-integration-key')

    from app.services import mcp_gateway
    tools = mcp_gateway.list_tools('live-test-server', tenant_id='gw-tenant')
    tool_names = {t['name'] for t in tools}
    assert {'health', 'ask_qarar', 'get_case', 'search_evidence', 'run_decision_council'} <= tool_names

    health_result = mcp_gateway.call_tool('live-test-server', 'health', {}, tenant_id='gw-tenant')
    assert health_result['is_error'] is False
    body = json.loads(health_result['content'][0])
    assert body['status'] == 'ok'
    assert body['tenant_id'] == 'gw-tenant'


def test_gateway_health_test_records_status(live_mcp_server, tmp_path, monkeypatch):
    from app.core.config import settings
    servers_file = _configure_gateway(tmp_path, live_mcp_server, with_auth=True)
    monkeypatch.setattr(settings, 'mcp_servers_file', str(servers_file))
    monkeypatch.setenv('GATEWAY_TEST_TOKEN', 'gw-integration-key')

    from app.services import mcp_gateway
    result = mcp_gateway.health_test('live-test-server', tenant_id='gw-tenant')
    assert result['status'] == 'ok'
    assert result['tool_count'] >= 5
