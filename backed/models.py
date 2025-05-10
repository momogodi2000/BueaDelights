from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} - {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"

class UserProfile(AbstractUser):
    """Custom user model extending AbstractUser"""
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('delivery', 'Delivery'),
        ('admin', 'Admin'),
    )
    
    phone_number = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    social_provider = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    REQUIRED_FIELDS = ['email']  # Add email as required field
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

class SessionActivity(models.Model):
    """Track user session activity for timeout functionality."""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40)
    last_activity = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'session_key')
        
    def __str__(self):
        return f"{self.user.username} - {self.session_key[:8]}"


class Category(models.Model):
    """Combined Category model with all needed fields"""
    CATEGORY_CHOICES = [
        ('chips', _('Chips')),
        ('juice', _('Jus naturels')),
        ('yogurt', _('Yaourts')),
        ('croquettes', _('Croquettes')),
        ('caramel', _('Caramels')),
        ('crepes', _('Crêpes')),
        ('pizza', _('Pizza')),
        ('nems', _('Nems')),
        ('pile', _('Pilé (plat traditionnel)')),
        ('cake', _('Gâteaux')),
        ('other', _('Autre')),
    ]
    
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    # Champ utilisé pour stocker le type prédéfini si sélectionné
    category_type = models.CharField(
        _('category type'),
        max_length=50, 
        choices=CATEGORY_CHOICES,
        default='other'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True, null=True)
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, 
        verbose_name=_('category'),
        related_name='products'
    )
    price = models.PositiveIntegerField(_('price (FCFA)'))
    stock_quantity = models.PositiveIntegerField(_('stock quantity'))
    ingredients = models.TextField(_('ingredients'), blank=True)
    image = models.ImageField(_('image'), upload_to='products/', null=True, blank=True)
    is_available = models.BooleanField(_('is available'), default=True)
    is_featured = models.BooleanField(_('is featured'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def availability_status(self):
        return _('Available') if self.is_available else _('Unavailable')
    
    @property
    def stock_status(self):
        if self.stock_quantity <= 0:
            return _('Out of stock')
        elif self.stock_quantity < 5:
            return _('Low stock')
        else:
            return _('In stock')


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='additional_images',
        verbose_name=_('product')
    )
    image = models.ImageField(_('image'), upload_to='products/gallery/')
    is_main = models.BooleanField(_('is main image'), default=False)
    alt_text = models.CharField(_('alternative text'), max_length=100, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')
        ordering = ['-is_main', '-created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"
    

# Order management models

class Order(models.Model):
    """Model for storing order information"""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('paid', _('Paid')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
    )
    
    user = models.ForeignKey(
        UserProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='orders',
        verbose_name=_('user')
    )
    full_name = models.CharField(_('full name'), max_length=100)
    email = models.EmailField(_('email'))
    phone_number = models.CharField(_('phone number'), max_length=15)
    address = models.TextField(_('delivery address'))
    city = models.CharField(_('city'), max_length=100)
    total_amount = models.PositiveIntegerField(_('total amount'))
    delivery_fee = models.PositiveIntegerField(_('delivery fee'), default=1000)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"
    
    @property
    def total_with_delivery(self):
        return self.total_amount + self.delivery_fee
    
    @property
    def item_count(self):
        return self.items.count()


class OrderItem(models.Model):
    """Model for storing order item details"""
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name=_('order')
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='order_items',
        verbose_name=_('product')
    )
    product_name = models.CharField(_('product name'), max_length=200)  # Store name in case product is deleted
    price = models.PositiveIntegerField(_('price'))  # Store price at time of purchase
    quantity = models.PositiveIntegerField(_('quantity'))
    
    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')
    
    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
    
    @property
    def subtotal(self):
        return self.price * self.quantity


class Transaction(models.Model):
    """Model for storing payment transaction information"""
    PAYMENT_METHOD_CHOICES = (
        ('noupia', 'Noupia'),
        ('momo', 'MTN Mobile Money'),
        ('om', 'Orange Money'),
        ('cash', 'Cash'),
    )
    
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    )
    
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='transactions',
        verbose_name=_('order')
    )
    transaction_id = models.CharField(_('transaction ID'), max_length=100, unique=True)
    payment_method = models.CharField(_('payment method'), max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.PositiveIntegerField(_('amount'))
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    provider_reference = models.CharField(_('provider reference'), max_length=100, blank=True)
    payment_details = models.JSONField(_('payment details'), default=dict, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_id} - {self.status}"


class SiteSettings(models.Model):
    """Model for storing site-wide settings"""
    site_name = models.CharField(_('site name'), max_length=100, default="BueaDelights")
    contact_email = models.EmailField(_('contact email'), default="folefacvivianekokobe@gmail.com")
    contact_phone = models.CharField(_('contact phone'), max_length=15, default="237699808260")
    whatsapp_number = models.CharField(_('WhatsApp number'), max_length=15, default="237699808260")
    delivery_fee = models.PositiveIntegerField(_('standard delivery fee'), default=1000)
    noupia_merchant_id = models.CharField(_('Noupia merchant ID'), max_length=100, blank=True)
    noupia_api_key = models.CharField(_('Noupia API key'), max_length=100, blank=True)
    noupia_api_secret = models.CharField(_('Noupia API secret'), max_length=100, blank=True)
    notification_emails = models.TextField(
        _('notification emails'), 
        help_text=_('Comma-separated list of email addresses to receive order notifications'),
        default="folefacvivianekokobe@gmail.com"
    )
    email_sender = models.EmailField(_('email sender address'), default="folefacvivianekokobe@gmail.com")
    email_password = models.CharField(_('email password'), max_length=100, blank=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('site settings')
        verbose_name_plural = _('site settings')
    
    def __str__(self):
        return self.site_name
    
    def get_notification_emails_list(self):
        """Returns a list of notification email addresses"""
        if not self.notification_emails:
            return []
        return [email.strip() for email in self.notification_emails.split(',')]
    
    @classmethod
    def get_settings(cls):
        """Get or create settings singleton"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update settings when SiteSettings are saved
        from django.conf import settings
        if self.noupia_api_key:
            settings.NOUPIA_API_KEY = self.noupia_api_key
        if self.noupia_merchant_id:
            settings.NOUPIA_MERCHANT_ID = self.noupia_merchant_id


