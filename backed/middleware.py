from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import resolve, reverse
from datetime import timedelta
import logging

from .models import SessionActivity

logger = logging.getLogger(__name__)

class SessionTimeoutMiddleware:
    """
    Middleware to handle session timeout after a period of inactivity.
    Automatically logs out users after 60 minutes of inactivity.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs that don't reset the activity timer
        self.exempt_urls = [
            'login',
            'logout',
            'register',
            'update_session_activity',
            'check_session_expired',
            'get_csrf_token',
        ]
    
    def __call__(self, request):
        # Don't process for non-authenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Skip processing for static files and certain URLs
        current_url = resolve(request.path_info).url_name
        if current_url in self.exempt_urls or request.path.startswith('/static/'):
            return self.get_response(request)
        
        # Get session key
        session_key = request.session.session_key
        if not session_key:
            # If there's no session key, we can't track activity
            return self.get_response(request)
        
        try:
            # Get user's session activity
            session_activity = SessionActivity.objects.get(
                user=request.user,
                session_key=session_key
            )
            
            # Check if session has timed out (60 minutes of inactivity)
            if timezone.now() > session_activity.last_activity + timedelta(minutes=60):
                # Expired session - log the user out
                logger.info(f"Session timed out for user {request.user.username}")
                logout(request)
                
                # If this is an AJAX request, return a 401 status
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': False, 
                        'expired': True, 
                        'message': 'Your session has expired. Please log in again.'
                    }, status=401)
                
                # Redirect to login with a message
                return redirect(reverse('login') + '?timeout=1')
            
            # Update last activity
            session_activity.last_activity = timezone.now()
            session_activity.save()
            
        except SessionActivity.DoesNotExist:
            # Create a new activity record
            SessionActivity.objects.create(
                user=request.user,
                session_key=session_key,
                last_activity=timezone.now()
            )
        
        return self.get_response(request)




