# payments/payment_service.py
import requests
import hmac
import hashlib
import time
from django.conf import settings
from django.urls import reverse
from urllib.parse import urljoin

class NoupiaPaymentService:
    
    @staticmethod
    def generate_signature(timestamp, merchant_id, transaction_id, amount):
        """Generate HMAC signature for Noupia API authentication"""
        string_to_sign = f"{timestamp}{merchant_id}{transaction_id}{amount}"
        return hmac.new(
            settings.NOUPIA_API_SECRET.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()

    @classmethod
    def initiate_payment(cls, order, customer_email, customer_phone):
        """Initiate payment with Noupia"""
        timestamp = str(int(time.time()))
        
        payload = {
            'merchant_id': settings.NOUPIA_MERCHANT_ID,
            'amount': order.total_with_delivery,
            'currency': 'XAF',
            'reference': order.id,
            'description': f'Payment for Order #{order.id}',
            'callback_url': settings.NOUPIA_CALLBACK_URL,
            'return_url': urljoin(
                settings.SITE_URL,
                reverse('payment_process', kwargs={'transaction_id': order.id})
            ),
            'customer': {
                'name': order.full_name,
                'email': customer_email,
                'phone': customer_phone
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'X-Noupia-Merchant-ID': settings.NOUPIA_MERCHANT_ID,
            'X-Noupia-API-Key': settings.NOUPIA_API_KEY,
            'X-Noupia-Timestamp': timestamp,
            'X-Noupia-Signature': cls.generate_signature(
                timestamp,
                settings.NOUPIA_MERCHANT_ID,
                order.id,
                order.total_with_delivery
            )
        }

        try:
            response = requests.post(
                f"{settings.NOUPIA_API_BASE_URL}/payments",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Log error and handle appropriately
            raise Exception(f"Noupia API request failed: {str(e)}")

    @classmethod
    def verify_payment(cls, transaction_id):
        """Verify payment status with Noupia"""
        timestamp = str(int(time.time()))
        
        headers = {
            'X-Noupia-Merchant-ID': settings.NOUPIA_MERCHANT_ID,
            'X-Noupia-API-Key': settings.NOUPIA_API_KEY,
            'X-Noupia-Timestamp': timestamp,
            'X-Noupia-Signature': cls.generate_signature(
                timestamp,
                settings.NOUPIA_MERCHANT_ID,
                transaction_id,
                ''
            )
        }

        try:
            response = requests.get(
                f"{settings.NOUPIA_API_BASE_URL}/payments/{transaction_id}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Payment verification failed: {str(e)}")