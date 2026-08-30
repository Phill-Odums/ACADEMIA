import hmac
import hashlib
import json
import uuid
import requests
from django.conf import settings
from django.urls import reverse

PAYSTACK_INITIALIZE_URL = "https://api.paystack.co/transaction/initialize"
PAYSTACK_VERIFY_URL = "https://api.paystack.co/transaction/verify/"

def initialize_paystack_payment(email, amount_in_naira, reference, callback_url, metadata=None):
    """
    Initializes a Paystack transaction.
    amount_in_naira is multiplied by 100 to convert to kobo.
    """
    if getattr(settings, 'PAYSTACK_DEMO_MODE', True) and (not settings.PAYSTACK_SECRET_KEY or 'placeholder' in settings.PAYSTACK_SECRET_KEY):
        # Demo simulation URL
        return {
            'status': True,
            'message': 'Demo initialization successful',
            'data': {
                'authorization_url': f"{callback_url}?reference={reference}&demo=true",
                'access_code': f"demo_code_{uuid.uuid4().hex[:10]}",
                'reference': reference
            }
        }

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "email": email,
        "amount": int(float(amount_in_naira) * 100),
        "reference": reference,
        "callback_url": callback_url,
        "metadata": metadata or {}
    }

    try:
        response = requests.post(PAYSTACK_INITIALIZE_URL, json=payload, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        return {'status': False, 'message': str(e)}

def verify_paystack_payment(reference):
    """
    Verifies a transaction using Paystack's verify endpoint.
    """
    if getattr(settings, 'PAYSTACK_DEMO_MODE', True) and (not settings.PAYSTACK_SECRET_KEY or 'placeholder' in settings.PAYSTACK_SECRET_KEY):
        return {
            'status': True,
            'message': 'Verification successful (Demo Mode)',
            'data': {
                'status': 'success',
                'reference': reference,
                'amount': 500000,
                'gateway_response': 'Successful',
            }
        }

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    try:
        response = requests.get(f"{PAYSTACK_VERIFY_URL}{reference}", headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        return {'status': False, 'message': str(e)}

def verify_paystack_webhook_signature(request_body_bytes, signature_header):
    """
    Verifies the Paystack webhook HMAC SHA512 signature.
    """
    if not signature_header or not settings.PAYSTACK_SECRET_KEY:
        return False
    computed_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
        request_body_bytes,
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(computed_signature, signature_header)
