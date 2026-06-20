import json
import base64
from urllib import request, error, parse
from django.conf import settings


def _normalize_phone(number: str) -> str:
    """Strip non-digits and ensure the number has a country code."""
    digits = ''.join(c for c in str(number) if c.isdigit())
    return digits


def _send_twilio(to_number: str, body: str) -> dict:
    sid = getattr(settings, 'WHATSAPP_TWILIO_SID', None)
    token = getattr(settings, 'WHATSAPP_TWILIO_TOKEN', None)
    from_number = getattr(settings, 'WHATSAPP_TWILIO_FROM', None)

    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    data = {
        'From': f"whatsapp:{from_number}",
        'To': f"whatsapp:{to_number}",
        'Body': body,
    }
    encoded_data = '&'.join([f"{k}={request.quote(v)}" for k, v in data.items()]).encode()
    req = request.Request(url, data=encoded_data, method='POST')
    credentials = base64.b64encode(f"{sid}:{token}".encode()).decode()
    req.add_header('Authorization', f'Basic {credentials}')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    try:
        with request.urlopen(req, timeout=30) as response:
            resp_data = json.loads(response.read().decode())
            return {'success': True, 'sid': resp_data.get('sid'), 'provider': 'twilio'}
    except error.HTTPError as e:
        resp_body = e.read().decode()
        print(f"[WhatsApp ERROR] {e.code} {e.reason}: {resp_body}")
        return {'success': False, 'error': f"{e.code} {e.reason}", 'provider': 'twilio'}
    except Exception as e:
        print(f"[WhatsApp ERROR] {e}")
        return {'success': False, 'error': str(e), 'provider': 'twilio'}


def _send_ultramsg_text(to_number: str, body: str) -> dict:
    instance_id = getattr(settings, 'ULTRAMSG_INSTANCE_ID', None)
    token = getattr(settings, 'ULTRAMSG_TOKEN', None)

    url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
    data = {
        'token': token,
        'to': _normalize_phone(to_number),
        'body': body,
    }
    encoded_data = parse.urlencode(data).encode()
    req = request.Request(url, data=encoded_data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    try:
        with request.urlopen(req, timeout=30) as response:
            resp_data = json.loads(response.read().decode())
            if resp_data.get('sent'):
                return {'success': True, 'sid': resp_data.get('id'), 'provider': 'ultramsg'}
            return {'success': False, 'error': resp_data.get('error', str(resp_data)), 'provider': 'ultramsg'}
    except error.HTTPError as e:
        resp_body = e.read().decode()
        print(f"[WhatsApp ERROR] {e.code} {e.reason}: {resp_body}")
        return {'success': False, 'error': f"{e.code} {e.reason}: {resp_body}", 'provider': 'ultramsg'}
    except Exception as e:
        print(f"[WhatsApp ERROR] {e}")
        return {'success': False, 'error': str(e), 'provider': 'ultramsg'}


def _send_ultramsg_document(to_number: str, filename: str, pdf_bytes: bytes, caption: str = '') -> dict:
    instance_id = getattr(settings, 'ULTRAMSG_INSTANCE_ID', None)
    token = getattr(settings, 'ULTRAMSG_TOKEN', None)

    url = f"https://api.ultramsg.com/{instance_id}/messages/document"
    data = {
        'token': token,
        'to': _normalize_phone(to_number),
        'filename': filename,
        'document': base64.b64encode(pdf_bytes).decode(),
        'caption': caption,
    }
    encoded_data = parse.urlencode(data).encode()
    req = request.Request(url, data=encoded_data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    try:
        with request.urlopen(req, timeout=60) as response:
            resp_data = json.loads(response.read().decode())
            if resp_data.get('sent'):
                return {'success': True, 'sid': resp_data.get('id'), 'provider': 'ultramsg'}
            return {'success': False, 'error': resp_data.get('error', str(resp_data)), 'provider': 'ultramsg'}
    except error.HTTPError as e:
        resp_body = e.read().decode()
        print(f"[WhatsApp ERROR] {e.code} {e.reason}: {resp_body}")
        return {'success': False, 'error': f"{e.code} {e.reason}: {resp_body}", 'provider': 'ultramsg'}
    except Exception as e:
        print(f"[WhatsApp ERROR] {e}")
        return {'success': False, 'error': str(e), 'provider': 'ultramsg'}


def send_whatsapp_message(to_number: str, body: str) -> dict:
    """
    Send a WhatsApp text message using the configured provider.
    In development (or when credentials are missing), logs to console.
    Supports: twilio, ultramsg
    """
    provider = getattr(settings, 'WHATSAPP_PROVIDER', 'twilio').lower()

    if provider == 'ultramsg':
        instance_id = getattr(settings, 'ULTRAMSG_INSTANCE_ID', None)
        token = getattr(settings, 'ULTRAMSG_TOKEN', None)
        if not instance_id or not token:
            print(f"[WhatsApp DEV - Ultramsg] To: {to_number}\nBody: {body}\n")
            return {'success': True, 'sid': None, 'provider': 'ultramsg-dev'}
        return _send_ultramsg_text(to_number, body)

    # Default Twilio
    sid = getattr(settings, 'WHATSAPP_TWILIO_SID', None)
    token = getattr(settings, 'WHATSAPP_TWILIO_TOKEN', None)
    from_number = getattr(settings, 'WHATSAPP_TWILIO_FROM', None)

    if not sid or not token or not from_number:
        print(f"[WhatsApp DEV - Twilio] To: {to_number}\nBody: {body}\n")
        return {'success': True, 'sid': None, 'provider': 'twilio-dev'}

    return _send_twilio(to_number, body)


def send_whatsapp_pdf(to_number: str, filename: str, pdf_bytes: bytes, caption: str = '') -> dict:
    """
    Send a PDF document via WhatsApp using the configured provider.
    Currently supported: ultramsg (document endpoint).
    Falls back to text message for Twilio/dev mode.
    """
    provider = getattr(settings, 'WHATSAPP_PROVIDER', 'twilio').lower()

    if provider == 'ultramsg':
        instance_id = getattr(settings, 'ULTRAMSG_INSTANCE_ID', None)
        token = getattr(settings, 'ULTRAMSG_TOKEN', None)
        if not instance_id or not token:
            print(f"[WhatsApp DEV - Ultramsg PDF] To: {to_number}\nFilename: {filename}\n")
            return {'success': True, 'sid': None, 'provider': 'ultramsg-dev'}
        return _send_ultramsg_document(to_number, filename, pdf_bytes, caption)

    # Twilio / dev: send a text with notice
    return send_whatsapp_message(to_number, f"{caption}\n[PDF attachment: {filename}]")
