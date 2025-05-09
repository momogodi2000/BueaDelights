from django.contrib import admin

# Register your models here.
# admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Product, Category, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'get_products_count')
    list_filter = ('category_type',)
    search_fields = ('name',)
    
    def get_products_count(self, obj):
        return obj.products.count()
    get_products_count.short_description = _('Products count')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'stock_status', 'is_available', 'is_featured')
    list_filter = ('category', 'is_available', 'is_featured')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]
    list_editable = ('price', 'stock_quantity', 'is_available', 'is_featured')
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'description')
        }),
        (_('Pricing and Stock'), {
            'fields': ('price', 'stock_quantity')
        }),
        (_('Details'), {
            'fields': ('ingredients', 'image')
        }),
        (_('Status'), {
            'fields': ('is_available', 'is_featured')
        }),
    )

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_main', 'alt_text', 'created_at')
    list_filter = ('is_main', 'created_at')
    search_fields = ('product__name', 'alt_text')