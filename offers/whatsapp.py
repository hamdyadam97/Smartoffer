import json
import base64
from urllib import request, error
from django.conf import settings


def send_whatsapp_message(to_number: str, body: str) -> dict:
    """
    Send a WhatsApp message.
    In development (or when Twilio credentials are missing), logs to console.
    In production with Twilio credentials, uses Twilio's Messages API.
    """
    sid = getattr(settings, 'WHATSAPP_TWILIO_SID', None)
    token = getattr(settings, 'WHATSAPP_TWILIO_TOKEN', None)
    from_number = getattr(settings, 'WHATSAPP_TWILIO_FROM', None)

    if not sid or not token or not from_number:
        print(f"[WhatsApp DEV] To: {to_number}\nBody: {body}\n")
        return {'success': True, 'sid': None, 'provider': 'console'}

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
