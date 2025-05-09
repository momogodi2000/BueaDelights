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



from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from .models import Product, Category
import json
import uuid
from datetime import timedelta
import requests
from reportlab.pdfgen import canvas
from io import BytesIO

def product_list(request):
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    
    products = Product.objects.filter(is_available=True)
    if category_id:
        products = products.filter(category_id=category_id)
    
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
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': int(category_id) if category_id else None,
        'cart_items': cart_items,
        'cart_total': total_price,
        'cart_count': len(cart_items),
        'delivery_fee': 1000,
        'whatsapp_number': '237695922065'
    }
    return render(request, 'products/product_list.html', context)

@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        product = Product.objects.get(id=product_id, is_available=True)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'})
    
    # Get or initialize cart in session
    cart = request.session.get('cart', {})
    
    if product_id in cart:
        cart[product_id]['quantity'] += quantity
    else:
        cart[product_id] = {
            'quantity': quantity,
            'added_at': timezone.now().isoformat()
        }
    
    request.session['cart'] = cart
    request.session.modified = True
    
    # Calculate new totals
    cart_count = len(cart)
    total_price = sum(
        Product.objects.get(id=p_id).price * item['quantity']
        for p_id, item in cart.items()
    )
    
    return JsonResponse({
        'success': True,
        'cart_count': cart_count,
        'total_price': total_price
    })

@require_POST
def update_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    
    cart = request.session.get('cart', {})
    
    if product_id in cart:
        if quantity > 0:
            cart[product_id]['quantity'] = quantity
        else:
            del cart[product_id]
        
        request.session['cart'] = cart
        request.session.modified = True
        
        # Calculate new totals
        cart_count = len(cart)
        total_price = sum(
            Product.objects.get(id=p_id).price * item['quantity']
            for p_id, item in cart.items()
        )
        
        return JsonResponse({
            'success': True,
            'cart_count': cart_count,
            'total_price': total_price
        })
    
    return JsonResponse({'success': False, 'error': 'Product not in cart'})

@require_POST
def remove_from_cart(request):
    product_id = request.POST.get('product_id')
    
    cart = request.session.get('cart', {})
    
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        request.session.modified = True
        
        # Calculate new totals
        cart_count = len(cart)
        total_price = sum(
            Product.objects.get(id=p_id).price * item['quantity']
            for p_id, item in cart.items()
        )
        
        return JsonResponse({
            'success': True,
            'cart_count': cart_count,
            'total_price': total_price
        })
    
    return JsonResponse({'success': False, 'error': 'Product not in cart'})

def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
    return redirect('product_list')

def checkout(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        return redirect('product_list')
    
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
    
    context = {
        'cart_items': cart_items,
        'subtotal': total_price,
        'delivery_fee': 1000,
        'total': total_price + 1000,
        'whatsapp_number': '237695922065'
    }
    return render(request, 'products/checkout.html', context)

def generate_whatsapp_link(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        return redirect('product_list')
    
    cart_items = []
    total_price = 0
    message = "Bonjour BueaDelights, je souhaite commander les produits suivants:\n\n"
    
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
    
    message += f"\nSous-total: {total_price} XAF\n"
    message += f"Frais de livraison: 1000 XAF\n"
    message += f"Total: {total_price + 1000} XAF\n\n"
    message += "Merci de me contacter pour finaliser la commande."
    
    whatsapp_url = f"https://wa.me/237695922065?text={requests.utils.quote(message)}"
    return redirect(whatsapp_url)

@csrf_exempt
def initiate_payment(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        
        if not cart:
            return JsonResponse({'success': False, 'error': 'Cart is empty'})
        
        # Calculate total amount
        total_amount = sum(
            Product.objects.get(id=p_id).price * item['quantity']
            for p_id, item in cart.items()
        ) + 1000  # Add delivery fee
        
        # Generate a unique transaction ID
        transaction_id = str(uuid.uuid4())
        
        # In a real implementation, you would call the Noupia API here
        # This is a mock implementation
        payment_data = {
            'transaction_id': transaction_id,
            'amount': total_amount,
            'status': 'pending',
            'timestamp': timezone.now().isoformat(),
            'cart': cart
        }
        
        # Store payment data in cache for 30 minutes
        cache.set(f'payment_{transaction_id}', payment_data, 1800)
        
        # In a real implementation, you would redirect to Noupia payment page
        # For this example, we'll simulate a successful payment
        return JsonResponse({
            'success': True,
            'transaction_id': transaction_id,
            'payment_url': f"/payment/process/{transaction_id}/"
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def payment_process(request, transaction_id):
    # In a real implementation, this would be the callback from Noupia
    # For this example, we'll simulate a successful payment
    
    payment_data = cache.get(f'payment_{transaction_id}')
    
    if not payment_data:
        return render(request, 'products/payment_error.html', {
            'error': 'Transaction not found or expired'
        })
    
    # Mark payment as successful
    payment_data['status'] = 'completed'
    cache.set(f'payment_{transaction_id}', payment_data, 1800)
    
    # Generate receipt
    receipt_data = generate_receipt(payment_data)
    
    # Clear cart
    if 'cart' in request.session:
        del request.session['cart']
    
    return render(request, 'products/payment_success.html', {
        'transaction_id': transaction_id,
        'receipt_data': receipt_data
    })

def generate_receipt(payment_data):
    # Create a PDF receipt
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    
    # Draw receipt content
    p.drawString(100, 800, "BueaDelights - Reçu de Paiement")
    p.drawString(100, 780, f"Transaction ID: {payment_data['transaction_id']}")
    p.drawString(100, 760, f"Date: {payment_data['timestamp']}")
    p.drawString(100, 740, "Détails de la commande:")
    
    y_position = 720
    for product_id, item in payment_data['cart'].items():
        product = Product.objects.get(id=product_id)
        p.drawString(120, y_position, f"- {product.name} x{item['quantity']} à {product.price} XAF")
        y_position -= 20
    
    p.drawString(100, y_position - 40, f"Sous-total: {payment_data['amount'] - 1000} XAF")
    p.drawString(100, y_position - 60, f"Frais de livraison: 1000 XAF")
    p.drawString(100, y_position - 80, f"Total: {payment_data['amount']} XAF")
    p.drawString(100, y_position - 120, "Merci pour votre commande!")
    
    p.showPage()
    p.save()
    
    # Get PDF content
    buffer.seek(0)
    return buffer


