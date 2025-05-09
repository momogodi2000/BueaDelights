from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
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

class Category(models.Model):
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['name']

    def __str__(self):
        return self.name

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
    # Champ utilisé pour stocker le type prédéfini si sélectionné
    category_type = models.CharField(
        _('category type'),
        max_length=50, 
        choices=CATEGORY_CHOICES,
        default='other'
    )
    
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
    

