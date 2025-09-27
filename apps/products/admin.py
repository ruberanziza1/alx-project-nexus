

# apps/products/admin.py

"""
Product Admin - Simplified (No Category model)
"""

from django.contrib import admin
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    """Inline admin for product images"""
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin for Product model"""
    
    list_display = [
        'name', 
        'category', 
        'price', 
        'stock_quantity', 
        'is_active', 
        'is_featured',
        'created_at'
    ]
    
    list_filter = [
        'category',
        'is_active', 
        'is_featured', 
        'created_at'
    ]
    
    search_fields = [
        'name', 
        'description', 
        'sku', 
        'category'
    ]
    
    readonly_fields = ['slug', 'sku', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price')
        }),
        ('Inventory', {
            'fields': ('sku', 'stock_quantity', 'low_stock_threshold')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline]
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).prefetch_related('images')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin for Product Images"""
    
    list_display = ['product', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name', 'alt_text']
    readonly_fields = ['created_at']