import email,imaplib
from email.header import decode_header
from app.core.config import settings

def _decode(v):
    if not v:return ''
    parts=[]
    for text,enc in decode_header(v):
        if isinstance(text,bytes): parts.append(text.decode(enc or 'utf-8',errors='replace'))
        else: parts.append(text)
    return ''.join(parts)

def _body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type()=='text/plain' and 'attachment' not in str(part.get('Content-Disposition','')).lower():
                b=part.get_payload(decode=True) or b''; return b.decode(part.get_content_charset() or 'utf-8',errors='replace')
        return ''
    b=msg.get_payload(decode=True) or b''; return b.decode(msg.get_content_charset() or 'utf-8',errors='replace')

def sync_imap(limit=25):
    if not (settings.imap_enabled and settings.imap_host and settings.imap_username and settings.imap_password):
        raise RuntimeError('IMAP connector is not configured')
    cls=imaplib.IMAP4_SSL if settings.imap_use_ssl else imaplib.IMAP4
    conn=cls(settings.imap_host,settings.imap_port)
    conn.login(settings.imap_username,settings.imap_password)
    conn.select(settings.imap_mailbox)
    _,data=conn.search(None,'ALL'); ids=(data[0].split() if data and data[0] else [])[-limit:]
    out=[]
    for mid in reversed(ids):
        _,raw=conn.fetch(mid,'(RFC822)')
        if not raw or not isinstance(raw[0],tuple):continue
        msg=email.message_from_bytes(raw[0][1])
        out.append({'message_id':mid.decode(),'subject':_decode(msg.get('Subject')),'from':_decode(msg.get('From')),'date':_decode(msg.get('Date')),'body':_body(msg)})
    try:conn.logout()
    except Exception:pass
    return out
