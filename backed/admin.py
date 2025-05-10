from django.contrib import admin
from .models import (
    ContactMessage, 
    NewsletterSubscriber, 
    UserProfile, 
    SessionActivity,
    Category,
    Product,
    ProductImage,
    Order,
    OrderItem,
    Transaction,
    SiteSettings
)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    date_hierarchy = 'created_at'
    list_per_page = 20


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at', 'is_active')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    date_hierarchy = 'subscribed_at'
    list_per_page = 50


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'date_joined')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    date_hierarchy = 'date_joined'


@admin.register(SessionActivity)
class SessionActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'last_activity', 'created_at')
    list_filter = ('last_activity', 'created_at')
    search_fields = ('user__username', 'session_key')
    date_hierarchy = 'last_activity'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'created_at')
    list_filter = ('category_type', 'created_at')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'is_available', 'is_featured')
    list_filter = ('category', 'is_available', 'is_featured', 'created_at')
    search_fields = ('name', 'description', 'ingredients')
    date_hierarchy = 'created_at'
    list_editable = ('price', 'stock_quantity', 'is_available', 'is_featured')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'category', 'price', 'ingredients')
        }),
        ('Stock Management', {
            'fields': ('stock_quantity', 'is_available')
        }),
        ('Display Options', {
            'fields': ('image', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_main', 'created_at')
    list_filter = ('is_main', 'created_at')
    search_fields = ('product__name', 'alt_text')
    date_hierarchy = 'created_at'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'city')
    search_fields = ('full_name', 'email', 'phone_number', 'address')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'status')
        }),
        ('Customer Information', {
            'fields': ('full_name', 'email', 'phone_number')
        }),
        ('Delivery Information', {
            'fields': ('address', 'city', 'notes')
        }),
        ('Financial Details', {
            'fields': ('total_amount', 'delivery_fee')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = []  # We'll add OrderItemInline here


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)


# Add OrderItemInline to OrderAdmin
OrderAdmin.inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'price', 'quantity', 'subtotal')
    list_filter = ('order__status',)
    search_fields = ('product_name', 'order__full_name')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'payment_method', 'amount', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'provider_reference', 'order__full_name')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'contact_email', 'updated_at')
    fieldsets = (
        ('General Settings', {
            'fields': ('site_name', 'contact_email', 'contact_phone', 'whatsapp_number')
        }),
        ('Delivery Settings', {
            'fields': ('delivery_fee',)
        }),
        ('Payment Integration', {
            'fields': ('noupia_merchant_id', 'noupia_api_key', 'noupia_api_secret'),
            'classes': ('collapse',)
        }),
        ('Email Settings', {
            'fields': ('notification_emails', 'email_sender', 'email_password'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance of SiteSettings
        return SiteSettings.objects.count() == 0
    
