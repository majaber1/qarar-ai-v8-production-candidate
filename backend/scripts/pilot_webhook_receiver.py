"""Minimal real webhook receiver standing in for a customer's n8n instance during pilot testing.

This is NOT a mock inside Qarar's own process — it is a separate real HTTP server that Qarar's
automation service posts to over the network, exactly as it would post to n8n. It then calls back
to Qarar's /api/connect/automation/callback/{run_id} endpoint, exactly as the committed
config/n8n_decision_to_action_workflow.json is designed to do once imported into a live n8n
instance. Use this to validate the Qarar side of the automation loop when a customer's n8n is not
yet available; swap N8N_WEBHOOK_BASE_URL for the real n8n endpoint for production.
"""
from __future__ import annotations
import json
import os
import sys
import httpx
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI(title='Qarar Pilot Webhook Receiver (n8n stand-in)')
CALLBACK_BASE = os.environ.get('QARAR_CALLBACK_BASE', 'http://127.0.0.1:8000')


@app.post('/webhook/{workflow_id}')
async def receive(workflow_id: str, request: Request):
    payload = await request.json()
    print(f'[pilot-webhook] received workflow={workflow_id} payload={json.dumps(payload)[:300]}', file=sys.stderr)
    callback_url = payload.get('qarar_callback_url')
    if callback_url:
        try:
            with httpx.Client(timeout=10) as c:
                c.post(callback_url, json={
                    'tenant_id': payload.get('tenant_id'),
                    'status': 'executed',
                    'detail': {'note': 'pilot webhook receiver simulated a project task creation', 'workflow_id': workflow_id},
                })
        except Exception as e:
            print(f'[pilot-webhook] callback failed: {e}', file=sys.stderr)
    return {'status': 'workflow_executed', 'received_case_id': payload.get('case_id')}


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=int(os.environ.get('PORT', 5679)))
