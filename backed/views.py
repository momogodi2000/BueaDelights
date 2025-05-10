from urllib import request
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import ContactMessage, NewsletterSubscriber
from .forms import ContactForm, NewsletterForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.conf import settings
from .models import UserProfile, SessionActivity
import json
import requests
from datetime import timedelta
import uuid
import logging
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.cache import cache
from .password_reset_utils import PasswordResetManager
import re
import json
from datetime import timedelta
from django.utils import timezone
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.db import transaction

from .models import Product, Category, ProductImage
from .forms import ProductForm, ProductImageFormSet

User = get_user_model()

# Set up logging
logger = logging.getLogger(__name__)

def home(request):
    contact_form = ContactForm(request.POST or None)
    newsletter_form = NewsletterForm(request.POST or None)
    
    if request.method == 'POST':
        if 'contact_submit' in request.POST:
            if contact_form.is_valid():
                try:
                    contact_message = contact_form.save()
                    print(f"Successfully saved contact message ID: {contact_message.id}")
                    messages.success(request, 'Thank you for your message! We will contact you soon.')
                    return redirect('home')
                except Exception as e:
                    print(f"Database error when saving contact: {str(e)}")
                    messages.error(request, 'An error occurred. Please try again later.')
            else:
                print("Contact form validation errors:", contact_form.errors)
                messages.error(request, 'Please correct the errors in the form.')
        
        elif 'newsletter_submit' in request.POST:
            if newsletter_form.is_valid():
                email = newsletter_form.cleaned_data['email']
                try:
                    subscriber, created = NewsletterSubscriber.objects.get_or_create(
                        email=email,
                        defaults={'is_active': True}
                    )
                    
                    if not created and not subscriber.is_active:
                        subscriber.is_active = True
                        subscriber.save()
                        messages.success(request, 'Welcome back! You have been resubscribed.')
                    elif not created:
                        messages.info(request, 'You are already subscribed.')
                    else:
                        messages.success(request, 'Thank you for subscribing!')
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                except Exception as e:
                    print(f"Error processing newsletter: {str(e)}")
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': str(e)})
                    messages.error(request, 'Subscription failed. Please try again.')
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'errors': newsletter_form.errors})
                messages.error(request, 'Invalid email address.')
    
    context = {
        'contact_form': contact_form,
        'newsletter_form': newsletter_form,
    }
    return render(request, 'LandingPage/homepage.html', context)

## login and register
def login_view(request):
    """Handle user login via traditional method or social authentication."""
    if request.method == 'POST':
        data = json.loads(request.body) if request.body else request.POST
        
        # Check if this is a social login
        if 'social_type' in data:
            return handle_social_login(request, data)
        
        # Traditional login
        email = data.get('email')
        password = data.get('password')
        remember_me = data.get('remember_me', False)
        
        if not email or not password:
            return JsonResponse({'success': False, 'message': 'Email and password are required'})
        
        try:
            # Django's username field is used for auth, but we store email
            user = UserProfile.objects.get(email=email)
            username = user.username
        except UserProfile.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid credentials'})
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            
            # Set or clear session expiry based on remember_me
            if remember_me:
                # Session will expire when browser is closed
                request.session.set_expiry(0)
            else:
                # Set session timeout to 60 minutes for inactivity
                request.session.set_expiry(3600)  # 60 minutes in seconds
            
            # Create or update session activity record
            SessionActivity.objects.update_or_create(
                user=user,
                session_key=request.session.session_key,
                defaults={
                    'last_activity': timezone.now(),
                }
            )
            
            # Get user role and prepare redirect URL
            redirect_url = get_redirect_url_by_role(user)
            
            return JsonResponse({
                'success': True, 
                'redirect': redirect_url,
                'role': user.role  # Directly access the role field
            })
        else:
            return JsonResponse({'success': False, 'message': 'Invalid credentials'})
            
    # For GET requests, render the login page
    return render(request, 'Authentication/login.html')

def register_view(request):
    """Handle user registration."""
    if request.method == 'POST':
        # Check content type to determine how to handle the data
        content_type = request.META.get('CONTENT_TYPE', '')
        
        if 'application/json' in content_type:
            # JSON data
            try:
                data = json.loads(request.body)
                # For file uploads with JSON, we need to handle them separately
                profile_picture = None  # No file uploads in JSON
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
        else:
            # Form data (multipart/form-data or application/x-www-form-urlencoded)
            data = request.POST.dict()
            profile_picture = request.FILES.get('profile_picture')
        
        # Extract registration data
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        # Validate inputs
        if not all([first_name, last_name, email, phone, password, confirm_password]):
            return JsonResponse({'success': False, 'message': 'All fields are required'})
        
        if password != confirm_password:
            return JsonResponse({'success': False, 'message': 'Passwords do not match'})
        
        # Check if email already exists
        if UserProfile.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Email already in use'})
        
        try:
            # Create username from first name, last name and random string
            username = f"{first_name.lower()}{last_name.lower()}{uuid.uuid4().hex[:8]}"
            
            # Create user with UserProfile model
            user = UserProfile.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone,
                role='client'  # Default role
            )
            
            # Add profile picture if provided
            if profile_picture:
                user.profile_picture = profile_picture
                user.save()
            
            return JsonResponse({'success': True, 'message': 'Registration successful. Please login.'})
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return JsonResponse({'success': False, 'message': 'An error occurred during registration'})
    
    # If GET request, redirect to login page with register tab active
    return redirect('/login/?tab=register')

def logout_view(request):
    """Handle user logout."""
    # Delete session activity record
    if request.user.is_authenticated and request.session.session_key:
        SessionActivity.objects.filter(
            user=request.user,
            session_key=request.session.session_key
        ).delete()
    
    # Log the user out
    logout(request)
    
    # Redirect to login page
    return redirect('login')

@csrf_exempt
def handle_social_login(request, data=None):
    """Process login with social providers (Google, Facebook)."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'})
    
    if not data:
        data = json.loads(request.body)
    
    social_type = data.get('social_type')
    token = data.get('token')
    
    if not social_type or not token:
        return JsonResponse({'success': False, 'message': 'Missing social login parameters'})
    
    try:
        if social_type == 'google':
            user_info = verify_google_token(token)
        elif social_type == 'facebook':
            user_info = verify_facebook_token(token)
        else:
            return JsonResponse({'success': False, 'message': 'Unsupported social provider'})
        
        if not user_info:
            return JsonResponse({'success': False, 'message': 'Invalid token'})
        
        # Get or create user based on email
        email = user_info.get('email')
        if not email:
            return JsonResponse({'success': False, 'message': 'Could not retrieve email from social provider'})
        
        try:
            user = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            # Create new user
            first_name = user_info.get('given_name', '') or user_info.get('first_name', '')
            last_name = user_info.get('family_name', '') or user_info.get('last_name', '')
            username = f"{first_name.lower()}{last_name.lower()}{uuid.uuid4().hex[:8]}"
            
            user = UserProfile.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number='',
                role='client',
                social_provider=social_type
            )
            
            # Set a random password that the user cannot use
            user.set_password(uuid.uuid4().hex)
            user.save()
        
        # Log in the user
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(request, user)
        
        # Set session timeout to 60 minutes for inactivity
        request.session.set_expiry(3600)
        
        # Create or update session activity record
        SessionActivity.objects.update_or_create(
            user=user,
            session_key=request.session.session_key,
            defaults={
                'last_activity': timezone.now(),
            }
        )
        
        # Get redirect URL based on user role
        redirect_url = get_redirect_url_by_role(user)
        
        return JsonResponse({
            'success': True, 
            'redirect': redirect_url,
            'role': user.role
        })
        
    except Exception as e:
        logger.error(f"Social login error: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Authentication failed'})

def verify_google_token(token):
    """Verify Google OAuth token and get user info."""
    try:
        # Google token verification endpoint
        response = requests.get(
            f'https://oauth2.googleapis.com/tokeninfo?id_token={token}'
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Google token verification error: {str(e)}")
        return None

def verify_facebook_token(token):
    """Verify Facebook OAuth token and get user info."""
    try:
        # Get user data with token
        graph_url = f'https://graph.facebook.com/me?fields=id,name,email,first_name,last_name&access_token={token}'
        response = requests.get(graph_url)
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Facebook token verification error: {str(e)}")
        return None

def get_redirect_url_by_role(user):
    """Get the correct redirect URL based on user role."""
    role = user.role  # Directly access the role attribute
    
    if role == 'admin':
        return '/adminpanel/'
    elif role == 'delivery':
        return '/delivery/'
    else:
        return '/client/'  # Default for clients

def update_session_activity(request):
    """Update the last activity timestamp for the session."""
    if request.user.is_authenticated and request.session.session_key:
        SessionActivity.objects.update_or_create(
            user=request.user,
            session_key=request.session.session_key,
            defaults={
                'last_activity': timezone.now(),
            }
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def check_session_expired(request):
    """Check if the current session has expired due to inactivity."""
    if request.user.is_authenticated and request.session.session_key:
        try:
            activity = SessionActivity.objects.get(
                user=request.user,
                session_key=request.session.session_key
            )
            
            # Check if last activity was more than 60 minutes ago
            if timezone.now() > activity.last_activity + timedelta(minutes=60):
                # Session has expired
                return JsonResponse({'expired': True})
                
        except SessionActivity.DoesNotExist:
            pass
    
    return JsonResponse({'expired': False})

def get_csrf_token(request):
    """Return a CSRF token for use in AJAX requests."""
    return JsonResponse({'csrfToken': get_token(request)})

@login_required
def profile_view(request):
    """Display and update user profile information."""
    if request.method == 'POST':
        # Handle profile update
        data = json.loads(request.body) if request.body else request.POST
        user = request.user
        
        # Update basic profile info
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.phone_number = data.get('phone', user.phone_number)
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        return JsonResponse({'success': True, 'message': 'Profile updated successfully'})
    
    # For GET requests, display the profile page
    return render(request, 'Authentication/profile.html', {'user': request.user})

## forget password

def forgot_password_form(request):
    """Render the forgot password HTML form"""
    return render(request, 'Authentication/forgot_password.html')

def verify_code_form(request):
    """Render the code verification HTML form"""
    identifier = request.GET.get('identifier', '')
    is_email = request.GET.get('is_email', 'true')
    return render(request, 'auth/verify_code.html', {
        'identifier': identifier,
        'is_email': is_email
    })

def reset_password_form(request):
    """Render the reset password HTML form"""
    reset_token = request.GET.get('token', '')
    return render(request, 'auth/reset_password.html', {
        'reset_token': reset_token
    })

@csrf_exempt
def forgot_password(request):
    if request.method == 'GET':
        return forgot_password_form(request)
    
    if request.method == 'POST':
        try:
            # Handle both form data and JSON data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                identifier = data.get('emailOrPhone', '').strip()
            else:
                identifier = request.POST.get('emailOrPhone', '').strip()
            
            if not identifier:
                return JsonResponse({'success': False, 'message': 'Email or phone number is required'})
            
            # Check if identifier is email or phone
            is_email = False
            try:
                validate_email(identifier)
                is_email = True
            except ValidationError:
                # Not an email, check if it's a valid phone number
                if not re.match(r'^\+?[0-9\s]{10,15}$', identifier):
                    return JsonResponse({'success': False, 'message': 'Invalid email or phone number format'})
            
            # Find user by email or phone
            user = None
            if is_email:
                try:
                    user = User.objects.get(email=identifier)
                except User.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'No user found with this email'})
            else:
                try:
                    user = User.objects.get(phone_number=identifier)
                except User.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'No user found with this phone number'})
            
            # Generate verification code
            code = PasswordResetManager.generate_verification_code()
            
            # Store the code
            PasswordResetManager.store_verification_code(identifier, code, is_email)
            
            # Send the code via email or SMS
            success = False
            if is_email:
                success = PasswordResetManager.send_verification_email(identifier, code)
            else:
                success = PasswordResetManager.send_verification_sms(identifier, code)
            
            if not success:
                return JsonResponse({'success': False, 'message': 'Failed to send verification code'})
            
            # Mask the identifier for display
            masked_identifier = mask_identifier(identifier, is_email)
            
            # For form submissions, redirect to verify code page
            if request.content_type != 'application/json':
                params = f'?identifier={identifier}&is_email={"true" if is_email else "false"}'
                return redirect(reverse('verify_reset_code') + params)
            
            # For API requests, return JSON
            return JsonResponse({
                'success': True,
                'message': 'Verification code sent',
                'is_email': is_email,
                'masked_identifier': masked_identifier
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def mask_identifier(identifier, is_email):
    """Mask the identifier for display (e.g., ex***@example.com or +237*****789)"""
    if is_email:
        parts = identifier.split('@')
        if len(parts) == 2:
            return f"{parts[0][:2]}***@{parts[1]}"
    else:
        if len(identifier) > 4:
            return f"{identifier[:3]}*****{identifier[-3:]}"
    return identifier

@csrf_exempt
def verify_reset_code(request):
    if request.method == 'GET':
        return verify_code_form(request)
    
    if request.method == 'POST':
        try:
            # Handle both form data and JSON data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                identifier = data.get('identifier', '').strip()
                code = data.get('code', '').strip()
            else:
                identifier = request.POST.get('identifier', '').strip()
                code = request.POST.get('code', '').strip()
            
            if not identifier or not code:
                return JsonResponse({'success': False, 'message': 'Identifier and code are required'})
            
            # Verify the code
            if PasswordResetManager.verify_code(identifier, code):
                # Generate a password reset token
                reset_token = PasswordResetManager.generate_verification_code(length=32)
                cache_key = f"pwd_reset_token:{reset_token}"
                cache.set(cache_key, identifier, timeout=600)  # 10 minutes expiration
                
                PasswordResetManager.clear_verification_code(identifier)
                
                # For form submissions, redirect to reset password page
                if request.content_type != 'application/json':
                    return redirect(reverse('reset_password') + f'?token={reset_token}')
                
                # For API requests, return JSON
                return JsonResponse({
                    'success': True,
                    'message': 'Code verified',
                    'reset_token': reset_token
                })
            else:
                return JsonResponse({'success': False, 'message': 'Invalid or expired verification code'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def reset_password(request):
    if request.method == 'GET':
        return reset_password_form(request)
    
    if request.method == 'POST':
        try:
            # Handle both form data and JSON data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                reset_token = data.get('reset_token', '').strip()
                new_password = data.get('new_password', '').strip()
                confirm_password = data.get('confirm_password', '').strip()
            else:
                reset_token = request.POST.get('reset_token', '').strip()
                new_password = request.POST.get('new_password', '').strip()
                confirm_password = request.POST.get('confirm_password', '').strip()
            
            if not reset_token or not new_password or not confirm_password:
                return JsonResponse({'success': False, 'message': 'All fields are required'})
            
            if new_password != confirm_password:
                return JsonResponse({'success': False, 'message': 'Passwords do not match'})
            
            # Validate password strength
            if len(new_password) < 8:
                return JsonResponse({'success': False, 'message': 'Password must be at least 8 characters'})
            
            if not any(char.isdigit() for char in new_password):
                return JsonResponse({'success': False, 'message': 'Password must contain at least one number'})
            
            if not any(char in '!@#$%^&*' for char in new_password):
                return JsonResponse({'success': False, 'message': 'Password must contain at least one special character'})
            
            # Verify reset token
            cache_key = f"pwd_reset_token:{reset_token}"
            identifier = cache.get(cache_key)
            
            if not identifier:
                return JsonResponse({'success': False, 'message': 'Invalid or expired reset token'})
            
            # Find user by email or phone
            try:
                validate_email(identifier)
                user = User.objects.get(email=identifier)
            except ValidationError:
                user = User.objects.get(phone_number=identifier)
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found'})
            
            # Update password
            user.set_password(new_password)
            user.save()
            
            # Clear the reset token
            cache.delete(cache_key)
            
            # For form submissions, redirect to login page
            if request.content_type != 'application/json':
                return redirect('login')
            
            # For API requests, return JSON
            return JsonResponse({'success': True, 'message': 'Password reset successfully'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})
    

## panel of user typer

@login_required
def adminpanel(request):
    return render(request, 'Dashboards/Admin/adminpanel.html')

@login_required
def delivery(request):
    return render(request, 'Dashboards/Delivery/deliverypanel.html')

@login_required
def client(request):
    return render(request, 'Dashboards/Clients/clientspanel.html')



#adminpanel
class ProductListView(ListView):
    model = Product
    template_name = 'Dashboards/Admin/product/product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductCreateView(SuccessMessageMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'Dashboards/Admin/product/add_product.html'
    success_url = reverse_lazy('products_list')
    success_message = _('Product was created successfully')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        
        if self.request.POST:
            context['image_formset'] = ProductImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['image_formset'] = ProductImageFormSet()
        
        return context
    
    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if image_formset.is_valid():
                image_formset.instance = self.object
                image_formset.save()
        
        return super().form_valid(form)


class ProductUpdateView(SuccessMessageMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'Dashboards/Admin/product/edit_product.html'
    success_url = reverse_lazy('products_list')
    success_message = _('Product was updated successfully')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        
        if self.request.POST:
            context['image_formset'] = ProductImageFormSet(
                self.request.POST, 
                self.request.FILES, 
                instance=self.object
            )
        else:
            context['image_formset'] = ProductImageFormSet(instance=self.object)
        
        return context
    
    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if image_formset.is_valid():
                image_formset.instance = self.object
                image_formset.save()
            else:
                return self.form_invalid(form)
        
        return super().form_valid(form)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'Dashboards/Admin/product/product_detail.html'
    context_object_name = 'product'


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'Dashboards/Admin/product/delete_product.html'
    success_url = reverse_lazy('products_list')
    success_message = _('Product was deleted successfully')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)






from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.urls import reverse
from django.db import transaction as db_transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

import json
import uuid
import requests
import hmac
import hashlib
import time
import yagmail
import os
import logging
from datetime import timedelta
from reportlab.pdfgen import canvas
from io import BytesIO

from .models import (
    Product, 
    Category, 
    Order, 
    OrderItem, 
    Transaction,
    SiteSettings,
    UserProfile
)

# Set up logging
logger = logging.getLogger(__name__)

def get_site_settings():
    """Helper function to get site settings"""
    return SiteSettings.get_settings()

# In your views.py
def product_list(request):
    """View function for listing products with optional category filtering"""
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    search_query = request.GET.get('search', '')
    
    products = Product.objects.filter(is_available=True)
    
    # Apply filters if provided
    if category_id:
        try:
            category_id = int(category_id)
            products = products.filter(category_id=category_id)
        except (ValueError, TypeError):
            pass  # Invalid category ID, ignore the filter
    
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get cart from session
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * item['quantity']
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'total': item_total
            })
            total_price += item_total
        except Product.DoesNotExist:
            continue
    
    # Get site settings
    site_settings = get_site_settings()
    
    context = {
        'products': page_obj,
        'categories': categories,
        'selected_category': int(category_id) if category_id else None,
        'search_query': search_query,
        'cart_items': cart_items,
        'cart_total': total_price,
        'cart_count': len(cart_items),
        'delivery_fee': site_settings.delivery_fee,
        'whatsapp_number': site_settings.whatsapp_number,
        'site_settings': site_settings,
    }
    return render(request, 'products/product_list.html', context)

def product_quick_view(request, product_id):
    """View function for quick product details view"""
    product = get_object_or_404(Product, id=product_id)
    
    context = {
        'product': product,
        'site_settings': get_site_settings()
    }
    return render(request, 'products/product_quick_view.html', context)


@require_POST
def add_to_cart(request):
    """View function to add product to cart"""
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        product = Product.objects.get(id=product_id, is_available=True)
        
        # Check stock
        if quantity > product.stock_quantity:
            return JsonResponse({
                'success': False, 
                'error': f'Only {product.stock_quantity} available in stock'
            })
            
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'})
    
    # Initialize or get cart from session
    cart = request.session.get('cart', {})
    
    if product_id in cart:
        # Update quantity if product already in cart
        new_quantity = cart[product_id]['quantity'] + quantity
        if new_quantity > product.stock_quantity:
            return JsonResponse({
                'success': False, 
                'error': f'Cannot add more. Only {product.stock_quantity} available'
            })
        cart[product_id]['quantity'] = new_quantity
    else:
        # Add new product to cart
        cart[product_id] = {
            'quantity': quantity,
            'added_at': timezone.now().isoformat()
        }
    
    # Save the cart back to session
    request.session['cart'] = cart
    request.session.modified = True
    
    # Calculate new cart totals
    cart_count = sum(item['quantity'] for item in cart.values())
    total_price = sum(
        Product.objects.get(id=p_id).price * item['quantity']
        for p_id, item in cart.items()
        if Product.objects.filter(id=p_id).exists()
    )
    
    return JsonResponse({
        'success': True,
        'cart_count': cart_count,
        'total_price': total_price,
        'message': f'{product.name} added to cart'
    })

@require_POST
def update_cart(request):
    """View function to update cart item quantity"""
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        product = Product.objects.get(id=product_id)
        
        # Check if stock is sufficient
        if quantity > product.stock_quantity:
            return JsonResponse({
                'success': False, 
                'error': f'Only {product.stock_quantity} available in stock'
            })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'})
    
    cart = request.session.get('cart', {})
    
    if product_id in cart:
        if quantity > 0:
            cart[product_id]['quantity'] = quantity
        else:
            del cart[product_id]
        
        request.session['cart'] = cart
        request.session.modified = True
        
        # Calculate new totals
        cart_count = sum(item['quantity'] for item in cart.values())
        total_price = 0
        for p_id, item in cart.items():
            try:
                p = Product.objects.get(id=p_id)
                total_price += p.price * item['quantity']
            except Product.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'cart_count': cart_count,
            'total_price': total_price,
            'product_total': product.price * quantity
        })
    
    return JsonResponse({'success': False, 'error': 'Product not in cart'})

@require_POST
def remove_from_cart(request):
    """View function to remove item from cart"""
    product_id = request.POST.get('product_id')
    
    cart = request.session.get('cart', {})
    
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        request.session.modified = True
        
        # Calculate new totals
        cart_count = sum(item['quantity'] for item in cart.values())
        total_price = 0
        for p_id, item in cart.items():
            try:
                p = Product.objects.get(id=p_id)
                total_price += p.price * item['quantity']
            except Product.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'cart_count': cart_count,
            'total_price': total_price
        })
    
    return JsonResponse({'success': False, 'error': 'Product not in cart'})

def clear_cart(request):
    """View function to clear the entire cart"""
    if 'cart' in request.session:
        del request.session['cart']
        messages.success(request, 'Cart has been cleared')
    return redirect('product_list')

def checkout(request):
    """View function for checkout page"""
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.warning(request, 'Your cart is empty')
        return redirect('product_list')
    
    cart_items = []
    total_price = 0
    
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            # Check if product is still available and has enough stock
            if not product.is_available or product.stock_quantity < item['quantity']:
                messages.warning(request, 
                    f'{product.name} is no longer available or has insufficient stock. Please update your cart.')
                return redirect('product_list')
                
            item_total = product.price * item['quantity']
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'total': item_total
            })
            total_price += item_total
        except Product.DoesNotExist:
            # Remove non-existent product from cart
            del cart[product_id]
            request.session.modified = True
            continue
    
    # Redirect if cart is empty after cleanup
    if not cart_items:
        messages.warning(request, 'Your cart is empty')
        return redirect('product_list')
    
    # Get site settings
    site_settings = get_site_settings()
    
    # Pre-fill form with user data if authenticated
    initial_data = {}
    if request.user.is_authenticated:
        user = request.user
        initial_data = {
            'full_name': user.get_full_name(),
            'email': user.email,
            'phone_number': user.phone_number,
        }
    
    context = {
        'cart_items': cart_items,
        'subtotal': total_price,
        'delivery_fee': site_settings.delivery_fee,
        'total': total_price + site_settings.delivery_fee,
        'whatsapp_number': site_settings.whatsapp_number,
        'initial_data': initial_data,
        'site_settings': site_settings,
    }
    return render(request, 'products/checkout.html', context)

def generate_whatsapp_link(request):
    """View function to generate WhatsApp order message"""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        
        if not cart:
            messages.warning(request, 'Your cart is empty')
            return redirect('product_list')
        
        # Get customer information from form
        full_name = request.POST.get('full_name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        notes = request.POST.get('notes', '')
        
        # Get site settings
        site_settings = get_site_settings()
        
        cart_items = []
        total_price = 0
        message = f"Bonjour BueaDelights, je souhaite commander les produits suivants:\n\n"
        
        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                item_total = product.price * item['quantity']
                cart_items.append({
                    'product': product,
                    'quantity': item['quantity'],
                    'total': item_total
                })
                total_price += item_total
                message += f"- {product.name} x{item['quantity']} à {product.price} XAF = {item_total} XAF\n"
            except Product.DoesNotExist:
                continue
        
        # Add customer information to message
        message += f"\nSous-total: {total_price} XAF\n"
        message += f"Frais de livraison: {site_settings.delivery_fee} XAF\n"
        message += f"Total: {total_price + site_settings.delivery_fee} XAF\n\n"
        
        message += "Mes informations:\n"
        message += f"Nom: {full_name}\n"
        message += f"Email: {email}\n"
        message += f"Téléphone: {phone}\n"
        message += f"Adresse: {address}\n"
        message += f"Ville: {city}\n"
        
        if notes:
            message += f"\nNotes: {notes}\n"
        
        message += "\nMerci de me contacter pour finaliser la commande."
        
        # Create order in database
        try:
            with db_transaction.atomic():
                # Create order
                order = Order.objects.create(
                    full_name=full_name,
                    email=email,
                    phone_number=phone,
                    address=address,
                    city=city,
                    notes=notes,
                    total_amount=total_price,
                    delivery_fee=site_settings.delivery_fee,
                    status='pending'
                )
                
                # Assign to user if authenticated
                if request.user.is_authenticated:
                    order.user = request.user
                    order.save()
                
                # Create order items
                for product_id, item in cart.items():
                    product = Product.objects.get(id=product_id)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        price=product.price,
                        quantity=item['quantity']
                    )
                
                # Send notification email
                try:
                    send_order_notification(order)
                except Exception as e:
                    logger.error(f"Failed to send order notification email: {e}")
                
                # Clear cart after successful order
                if 'cart' in request.session:
                    del request.session['cart']
                
                # Generate WhatsApp URL
                whatsapp_url = f"https://wa.me/{site_settings.whatsapp_number.lstrip('+')}" \
                              f"?text={requests.utils.quote(message)}"
                
                return redirect(whatsapp_url)
                
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            messages.error(request, "An error occurred while processing your order. Please try again.")
            return redirect('checkout')
    
    return redirect('checkout')

@csrf_exempt
def initiate_payment(request):
    """View function to initiate Noupia payment"""
    if request.method == 'POST':
        # Get cart and validate
        cart = request.session.get('cart', {})
        
        if not cart:
            return JsonResponse({'success': False, 'error': 'Cart is empty'})
        
        # Get customer information from form
        data = json.loads(request.body)
        full_name = data.get('full_name', '')
        email = data.get('email', '')
        phone = data.get('phone', '')
        address = data.get('address', '')
        city = data.get('city', '')
        notes = data.get('notes', '')
        
        # Validate required fields
        if not all([full_name, email, phone, address, city]):
            return JsonResponse({
                'success': False, 
                'error': 'Please fill in all required fields'
            })
        
        # Get site settings
        site_settings = get_site_settings()
        
        # Calculate total amount
        cart_items = []
        subtotal = 0
        
        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                if not product.is_available or product.stock_quantity < item['quantity']:
                    return JsonResponse({
                        'success': False, 
                        'error': f'{product.name} is no longer available or has insufficient stock'
                    })
                
                item_total = product.price * item['quantity']
                cart_items.append({
                    'product': product,
                    'quantity': item['quantity'],
                    'total': item_total
                })
                subtotal += item_total
            except Product.DoesNotExist:
                continue
        
        if not cart_items:
            return JsonResponse({'success': False, 'error': 'No valid items in cart'})
        
        total_amount = subtotal + site_settings.delivery_fee
        
        try:
            with db_transaction.atomic():
                # Create order
                order = Order.objects.create(
                    full_name=full_name,
                    email=email,
                    phone_number=phone,
                    address=address,
                    city=city,
                    notes=notes,
                    total_amount=subtotal,
                    delivery_fee=site_settings.delivery_fee,
                    status='pending'
                )
                
                # Assign to user if authenticated
                if request.user.is_authenticated:
                    order.user = request.user
                    order.save()
                
                # Create order items
                for product_id, item in cart.items():
                    product = Product.objects.get(id=product_id)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        price=product.price,
                        quantity=item['quantity']
                    )
                
                # Generate a unique transaction ID
                transaction_id = str(uuid.uuid4())
                
                # Create transaction record
                transaction = Transaction.objects.create(
                    order=order,
                    transaction_id=transaction_id,
                    payment_method='noupia',
                    amount=total_amount,
                    status='pending'
                )
                
                # Call Noupia API
                noupia_response = initiate_noupia_payment(
                    transaction_id=transaction_id,
                    amount=total_amount,
                    email=email,
                    phone=phone,
                    customer_name=full_name,
                    site_settings=site_settings
                )
                
                if noupia_response.get('status') == 'success':
                    # Store payment data
                    transaction.provider_reference = noupia_response.get('reference', '')
                    transaction.payment_details = noupia_response
                    transaction.save()
                    
                    # Clear cart after initiating payment
                    if 'cart' in request.session:
                        del request.session['cart']
                    
                    # Return payment URL and transaction ID
                    return JsonResponse({
                        'success': True,
                        'transaction_id': transaction_id,
                        'payment_url': noupia_response.get('payment_url'),
                        'message': 'Payment initiated successfully'
                    })
                else:
                    # Handle Noupia API error
                    error_message = noupia_response.get('message', 'Payment initiation failed')
                    transaction.status = 'failed'
                    transaction.payment_details = {
                        'error': error_message,
                        'response': noupia_response
                    }
                    transaction.save()
                    
                    return JsonResponse({
                        'success': False,
                        'error': error_message
                    })
                
        except Exception as e:
            logger.error(f"Error initiating payment: {e}")
            return JsonResponse({
                'success': False,
                'error': 'An unexpected error occurred. Please try again.'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def noupia_webhook(request):
    """Webhook endpoint for Noupia payment notifications"""
    if request.method == 'POST':
        try:
            # Get site settings
            site_settings = get_site_settings()
            
            # Get request data
            payload = json.loads(request.body)
            logger.info(f"Received Noupia webhook: {payload}")
            
            # Verify webhook signature if provided
            signature = request.headers.get('Noupia-Signature')
            if signature and site_settings.noupia_api_secret:
                computed_signature = hmac.new(
                    site_settings.noupia_api_secret.encode(),
                    request.body,
                    hashlib.sha256
                ).hexdigest()
                
                if not hmac.compare_digest(signature, computed_signature):
                    logger.warning("Invalid Noupia webhook signature")
                    return HttpResponse(status=401)
            
            # Extract transaction information
            transaction_id = payload.get('transaction_id')
            status = payload.get('status')
            provider_reference = payload.get('reference')
            
            if not transaction_id or not status:
                return HttpResponse(status=400)
            
            # Update transaction and order
            with db_transaction.atomic():
                try:
                    transaction = Transaction.objects.get(transaction_id=transaction_id)
                except Transaction.DoesNotExist:
                    logger.warning(f"Transaction not found: {transaction_id}")
                    return HttpResponse(status=404)
                
                order = transaction.order
                
                # Update transaction status
                if status.lower() in ['success', 'completed', 'paid']:
                    transaction.status = 'completed'
                    order.status = 'paid'
                elif status.lower() in ['failed', 'declined', 'rejected']:
                    transaction.status = 'failed'
                elif status.lower() in ['cancelled']:
                    transaction.status = 'cancelled'
                    
                # Update provider reference if provided
                if provider_reference:
                    transaction.provider_reference = provider_reference
                
                # Save payment details
                transaction.payment_details = {
                    **transaction.payment_details,
                    'webhook_data': payload,
                    'webhook_received_at': timezone.now().isoformat()
                }
                
                transaction.save()
                order.save()
                
                # Send notification email if payment is completed
                if transaction.status == 'completed':
                    try:
                        send_payment_confirmation(order, transaction)
                    except Exception as e:
                        logger.error(f"Failed to send payment confirmation email: {e}")
                
                # Update product stock quantities if payment is completed
                if transaction.status == 'completed':
                    for order_item in order.items.all():
                        if order_item.product:
                            product = order_item.product
                            product.stock_quantity = max(0, product.stock_quantity - order_item.quantity)
                            product.save()
                
            return HttpResponse(status=200)
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook payload")
            return HttpResponse(status=400)
        except Exception as e:
            logger.error(f"Error processing Noupia webhook: {e}")
            return HttpResponse(status=500)
    
    return HttpResponse(status=405)

def payment_process(request, transaction_id):
    """View function to handle payment processing and status page"""
    try:
        transaction = Transaction.objects.get(transaction_id=transaction_id)
    except Transaction.DoesNotExist:
        messages.error(request, "Transaction not found")
        return redirect('product_list')
    
    order = transaction.order
    
    # Check payment status
    if transaction.status == 'pending':
        # Check with Noupia API for status update
        updated_status = check_payment_status(transaction)
        
        if updated_status != transaction.status:
            transaction.status = updated_status
            transaction.save()
            
            if updated_status == 'completed':
                order.status = 'paid'
                order.save()
                
                # Send notification email
                try:
                    send_payment_confirmation(order, transaction)
                except Exception as e:
                    logger.error(f"Failed to send payment confirmation email: {e}")
                
                # Update product stock quantities
                for order_item in order.items.all():
                    if order_item.product:
                        product = order_item.product
                        product.stock_quantity = max(0, product.stock_quantity - order_item.quantity)
                        product.save()
    
    # Render appropriate template based on payment status
    if transaction.status == 'completed':
        # Generate receipt data
        receipt_data = generate_receipt(order, transaction)
        
        return render(request, 'products/payment_success.html', {
            'order': order,
            'transaction': transaction,
            'receipt_data': receipt_data
        })
    elif transaction.status == 'failed':
        return render(request, 'products/payment_failed.html', {
            'order': order,
            'transaction': transaction
        })
    else:
        # Still pending
        return render(request, 'products/payment_pending.html', {
            'order': order,
            'transaction': transaction
        })

def download_receipt(request, transaction_id):
    """View function to download PDF receipt"""
    try:
        transaction = Transaction.objects.get(transaction_id=transaction_id)
    except Transaction.DoesNotExist:
        messages.error(request, "Transaction not found")
        return redirect('product_list')
    
    if transaction.status != 'completed':
        messages.error(request, "Receipt is only available for completed payments")
        return redirect('product_list')
    
    # Generate PDF receipt
    buffer = generate_receipt_pdf(transaction.order, transaction)
    
    # Create response with PDF
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{transaction_id}.pdf"'
    
    return response

@login_required
def order_history(request):
    """View function for user's order history"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
    }
    return render(request, 'products/order_history.html', context)

@login_required
def order_detail(request, order_id):
    """View function for order details"""
    order = get_object_or_404(Order, id=order_id)
    
    # Security check - users can only view their own orders unless they're staff
    if order.user != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to view this order")
        return redirect('order_history')
    
    context = {
        'order': order,
        'order_items': order.items.all(),
        'transactions': order.transactions.all()
    }
    return render(request, 'products/order_detail.html', context)

# Helper functions

def initiate_noupia_payment(transaction_id, amount, email, phone, customer_name, site_settings):
    """
    Helper function to initiate payment with Noupia API
    
    Returns:
    {
        'status': 'success' or 'error',
        'reference': 'NP123456', # Noupia reference
        'payment_url': 'https://noupia.com/pay/...',
        'message': 'Success' or error message
    }
    """
    try:
        # Noupia API endpoint
        api_url = "https://api.noupia.com/v1/payments"
        
        # Prepare payment data
        payload = {
            'merchant_id': site_settings.noupia_merchant_id,
            'amount': amount,
            'currency': 'XAF',
            'reference': transaction_id,
            'description': f'Payment for BueaDelights order',
            'callback_url': request.build_absolute_uri(reverse('noupia_webhook')),
            'return_url': request.build_absolute_uri(
                reverse('payment_process', kwargs={'transaction_id': transaction_id})
            ),
            'customer': {
                'name': customer_name,
                'email': email,
                'phone': phone
            }
        }
        
        # Calculate signature for authentication
        timestamp = str(int(time.time()))
        string_to_sign = f"{timestamp}{site_settings.noupia_merchant_id}{transaction_id}{amount}"
        signature = hmac.new(
            site_settings.noupia_api_secret.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Set headers
        headers = {
            'Content-Type': 'application/json',
            'X-Noupia-Merchant-ID': site_settings.noupia_merchant_id,
            'X-Noupia-API-Key': site_settings.noupia_api_key,
            'X-Noupia-Timestamp': timestamp,
            'X-Noupia-Signature': signature
        }
        
        # Make API request
        response = requests.post(api_url, json=payload, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('status') == 'success':
            return {
                'status': 'success',
                'reference': response_data.get('reference'),
                'payment_url': response_data.get('payment_url'),
                'message': 'Payment initiated successfully'
            }
        else:
            logger.error(f"Noupia API error: {response_data}")
            return {
                'status': 'error',
                'message': response_data.get('message', 'Payment initiation failed'),
                'details': response_data
            }
    
    except Exception as e:
        logger.error(f"Error in Noupia payment initiation: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def check_payment_status(transaction):
    """
    Check payment status with Noupia API
    
    Returns:
    'pending', 'completed', 'failed', or 'cancelled'
    """
    try:
        site_settings = get_site_settings()
        
        # Noupia API endpoint for checking payment status
        api_url = f"https://api.noupia.com/v1/payments/{transaction.transaction_id}"
        
        # Calculate signature for authentication
        timestamp = str(int(time.time()))
        string_to_sign = f"{timestamp}{site_settings.noupia_merchant_id}{transaction.transaction_id}"
        signature = hmac.new(
            site_settings.noupia_api_secret.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Set headers
        headers = {
            'X-Noupia-Merchant-ID': site_settings.noupia_merchant_id,
            'X-Noupia-API-Key': site_settings.noupia_api_key,
            'X-Noupia-Timestamp': timestamp,
            'X-Noupia-Signature': signature
        }
        
        # Make API request
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200:
            noupia_status = response_data.get('status', '').lower()
            
            # Map Noupia status to our status
            if noupia_status in ['success', 'completed', 'paid']:
                return 'completed'
            elif noupia_status in ['failed', 'declined', 'rejected']:
                return 'failed'
            elif noupia_status in ['cancelled']:
                return 'cancelled'
            else:
                return 'pending'
        else:
            logger.error(f"Error checking payment status: {response_data}")
            return transaction.status
            
    except Exception as e:
        logger.error(f"Error checking payment status: {e}")
        return transaction.status

def send_order_notification(order):
    """Send email notification about new order"""
    site_settings = get_site_settings()
    
    try:
        # Initialize yagmail
        yag = yagmail.SMTP(
            user=site_settings.email_sender,
            password=site_settings.email_password
        )
        
        # Prepare email content
        subject = f'New Order #{order.id} from {order.full_name}'
        
        # Build HTML content
        html_content = f"""
        <h2>New Order #{order.id}</h2>
        <p><strong>Customer:</strong> {order.full_name}</p>
        <p><strong>Email:</strong> {order.email}</p>
        <p><strong>Phone:</strong> {order.phone_number}</p>
        <p><strong>Address:</strong> {order.address}, {order.city}</p>
        <p><strong>Order Date:</strong> {order.created_at.strftime('%Y-%m-%d %H:%M')}</p>
        
        <h3>Order Items:</h3>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
            <tr>
                <th>Product</th>
                <th>Price</th>
                <th>Quantity</th>
                <th>Subtotal</th>
            </tr>
        """
        
        for item in order.items.all():
            html_content += f"""
            <tr>
                <td>{item.product_name}</td>
                <td>{item.price} XAF</td>
                <td>{item.quantity}</td>
                <td>{item.price * item.quantity} XAF</td>
            </tr>
            """
        
        html_content += f"""
        </table>
        
        <p><strong>Subtotal:</strong> {order.total_amount} XAF</p>
        <p><strong>Delivery Fee:</strong> {order.delivery_fee} XAF</p>
        <p><strong>Total:</strong> {order.total_amount + order.delivery_fee} XAF</p>
        
        <p><strong>Notes:</strong> {order.notes}</p>
        
        <p>This order is awaiting payment/confirmation.</p>
        """
        
        # Send email to all notification recipients
        recipients = site_settings.get_notification_emails_list()
        if recipients:
            yag.send(
                to=recipients,
                subject=subject,
                contents=html_content
            )
            logger.info(f"Order notification sent for Order #{order.id}")
        else:
            logger.warning("No notification recipients configured")
    
    except Exception as e:
        logger.error(f"Error sending order notification email: {e}")
        raise

def send_payment_confirmation(order, transaction):
    """Send email notification about successful payment"""
    site_settings = get_site_settings()
    
    try:
        # Initialize yagmail
        yag = yagmail.SMTP(
            user=site_settings.email_sender,
            password=site_settings.email_password
        )
        
        # Prepare email content
        subject = f'Payment Confirmed for Order #{order.id}'
        
        # Build HTML content
        html_content = f"""
        <h2>Payment Confirmed for Order #{order.id}</h2>
        <p><strong>Customer:</strong> {order.full_name}</p>
        <p><strong>Transaction ID:</strong> {transaction.transaction_id}</p>
        <p><strong>Payment Method:</strong> {transaction.get_payment_method_display()}</p>
        <p><strong>Amount:</strong> {transaction.amount} XAF</p>
        <p><strong>Payment Date:</strong> {transaction.updated_at.strftime('%Y-%m-%d %H:%M')}</p>
        
        <h3>Order Items:</h3>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
            <tr>
                <th>Product</th>
                <th>Price</th>
                <th>Quantity</th>
                <th>Subtotal</th>
            </tr>
        """
        
        for item in order.items.all():
            html_content += f"""
            <tr>
                <td>{item.product_name}</td>
                <td>{item.price} XAF</td>
                <td>{item.quantity}</td>
                <td>{item.price * item.quantity} XAF</td>
            </tr>
            """
        
        html_content += f"""
        </table>
        
        <p><strong>Subtotal:</strong> {order.total_amount} XAF</p>
        <p><strong>Delivery Fee:</strong> {order.delivery_fee} XAF</p>
        <p><strong>Total:</strong> {order.total_amount + order.delivery_fee} XAF</p>
        
        <p>This order has been paid and is ready for processing.</p>
        """
        
        # Send email to all notification recipients
        recipients = site_settings.get_notification_emails_list()
        if recipients:
            yag.send(
                to=recipients,
                subject=subject,
                contents=html_content
            )
            logger.info(f"Payment confirmation sent for Order #{order.id}")
        else:
            logger.warning("No notification recipients configured")
    
    except Exception as e:
        logger.error(f"Error sending payment confirmation email: {e}")
        raise

def generate_receipt(order, transaction):
    """Generate receipt data for display"""
    receipt_data = {
        'order_id': order.id,
        'transaction_id': transaction.transaction_id,
        'payment_date': transaction.updated_at,
        'customer': order.full_name,
        'email': order.email,
        'phone': order.phone_number,
        'address': f"{order.address}, {order.city}",
        'items': [
            {
                'name': item.product_name,
                'price': item.price,
                'quantity': item.quantity,
                'subtotal': item.price * item.quantity
            }
            for item in order.items.all()
        ],
        'subtotal': order.total_amount,
        'delivery_fee': order.delivery_fee,
        'total': order.total_amount + order.delivery_fee
    }
    
    return receipt_data

def generate_receipt_pdf(order, transaction):
    """Generate PDF receipt"""
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    
    # Set title
    p.setTitle(f"BueaDelights - Receipt #{order.id}")
    
    # Draw receipt content
    y_position = 800
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, y_position, "BueaDelights - Receipt")
    y_position -= 30
    
    # Order information
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y_position, "Order Information")
    y_position -= 20
    
    # Order details
    p.setFont("Helvetica", 10)
    p.drawString(100, y_position, f"Order #: {order.id}")
    y_position -= 15
    p.drawString(100, y_position, f"Transaction ID: {transaction.transaction_id}")
    y_position -= 15
    p.drawString(100, y_position, f"Date: {transaction.updated_at.strftime('%Y-%m-%d %H:%M')}")
    y_position -= 15
    p.drawString(100, y_position, f"Payment Method: {transaction.get_payment_method_display()}")
    y_position -= 30
    
    # Customer information
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y_position, "Customer Information")
    y_position -= 20
    
    p.setFont("Helvetica", 10)
    p.drawString(100, y_position, f"Name: {order.full_name}")
    y_position -= 15
    p.drawString(100, y_position, f"Email: {order.email}")
    y_position -= 15
    p.drawString(100, y_position, f"Phone: {order.phone_number}")
    y_position -= 15
    p.drawString(100, y_position, f"Address: {order.address}, {order.city}")
    y_position -= 30
    
    # Order items
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y_position, "Order Items")
    y_position -= 20
    
    # Table header
    p.setFont("Helvetica-Bold", 10)
    p.drawString(100, y_position, "Product")
    p.drawString(300, y_position, "Price")
    p.drawString(350, y_position, "Qty")
    p.drawString(400, y_position, "Subtotal")
    y_position -= 15
    
    # Draw a line
    p.line(100, y_position, 500, y_position)
    y_position -= 15
    
    # Table content
    p.setFont("Helvetica", 10)
    for item in order.items.all():
        p.drawString(100, y_position, item.product_name[:30])  # Limit to 30 chars
        p.drawString(300, y_position, f"{item.price} XAF")
        p.drawString(350, y_position, str(item.quantity))
        p.drawString(400, y_position, f"{item.price * item.quantity} XAF")
        y_position -= 15
    
    # Draw a line
    y_position -= 10
    p.line(100, y_position, 500, y_position)
    y_position -= 20
    
    # Totals
    p.drawString(300, y_position, "Subtotal:")
    p.drawString(400, y_position, f"{order.total_amount} XAF")
    y_position -= 15
    
    p.drawString(300, y_position, "Delivery Fee:")
    p.drawString(400, y_position, f"{order.delivery_fee} XAF")
    y_position -= 15
    
    p.setFont("Helvetica-Bold", 10)
    p.drawString(300, y_position, "Total:")
    p.drawString(400, y_position, f"{order.total_amount + order.delivery_fee} XAF")
    y_position -= 30
    
    # Footer
    p.setFont("Helvetica", 10)
    p.drawString(100, y_position, "Thank you for your order!")
    y_position -= 15
    p.drawString(100, y_position, f"For any questions, please contact us at: {SiteSettings.get_settings().contact_email}")
    
    p.showPage()
    p.save()
    
    # Get PDF content
    buffer.seek(0)
    return buffer



    