import random
import string
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache
import yagmail
import requests
import json
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class PasswordResetManager:
    @staticmethod
    def generate_verification_code(length=6):
        """Generate a random numeric verification code."""
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def send_verification_email(email, code):
        """Send verification code via email using yagmail."""
        try:
            subject = "BueaDelights - Password Reset Verification Code"
            contents = [
                f"Your password reset verification code is: <strong>{code}</strong>",
                "This code will expire in 10 minutes.",
                "If you didn't request this, please ignore this email."
            ]
            
            with yagmail.SMTP(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD) as yag:
                yag.send(email, subject, contents)
            
            return True
        except Exception as e:
            logger.error(f"Error sending verification email: {str(e)}")
            return False

    @staticmethod
    def send_verification_sms(phone_number, code):
        """Send verification code via SMS using Infobip."""
        try:
            url = f"{settings.INFOBIP_BASE_URL}/sms/2/text/advanced"
            headers = {
                'Authorization': f'App {settings.INFOBIP_API_KEY}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            payload = {
                "messages": [
                    {
                        "destinations": [{"to": phone_number}],
                        "from": settings.INFOBIP_SENDER_ID,
                        "text": f"Your BueaDelights verification code is: {code}. Valid for 10 minutes."
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error sending verification SMS: {str(e)}")
            return False

    @staticmethod
    def store_verification_code(identifier, code, is_email=True):
        """Store verification code in cache with expiration."""
        key = f"pwd_reset:{identifier}"
        # Store for 10 minutes (600 seconds)
        cache.set(key, {
            'code': code,
            'is_email': is_email,
            'created_at': timezone.now().isoformat()
        }, timeout=600)
        return True

    @staticmethod
    def verify_code(identifier, user_code):
        """Verify if the provided code matches the stored one."""
        key = f"pwd_reset:{identifier}"
        stored_data = cache.get(key)
        
        if not stored_data:
            return False
        
        return stored_data['code'] == user_code

    @staticmethod
    def clear_verification_code(identifier):
        """Clear the verification code from cache."""
        key = f"pwd_reset:{identifier}"
        cache.delete(key)



