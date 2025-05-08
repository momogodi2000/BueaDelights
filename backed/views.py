from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import ContactMessage, NewsletterSubscriber
from .forms import ContactForm, NewsletterForm

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



def login(request):
    return render(request, 'Authentication/login.html')

def logout(request):
    return render(request, 'Authentication/logout.html')


def forgot_password(request):
    return render(request, 'Authentication/forgot_password.html')

def adminpanel(request):
    return render(request, 'Dashboards/Admin/adminpanel.html')

def delivery(request):
    return render(request, 'Dashboards/Delivery/deliverypanel.html')

def client(request):
    return render(request, 'Dashboards/Clients/clientspanel.html')
