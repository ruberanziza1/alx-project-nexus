# apps/orders/admin.py

"""
Order Admin Configuration
"""

from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items"""
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'product_sku', 'quantity', 'unit_price', 'subtotal', 'created_at']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for Order model"""
    
    list_display = [
        'id',
        'user',
        'status',
        'total_amount',
        'total_items',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'created_at'
    ]
    
    search_fields = [
        'user__email',
        'id',
        'shipping_city'
    ]
    
    readonly_fields = [
        'id',
        'user',
        'subtotal',
        'total_amount',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'user', 'status', 'subtotal', 'total_amount')
        }),
        ('Shipping Details', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_country', 'shipping_postal_code')
        }),
        ('Notes', {
            'fields': ('order_notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrderItemInline]
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user').prefetch_related('items')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin for Order Items"""
    
    list_display = ['order', 'product_name', 'quantity', 'unit_price', 'subtotal']
    list_filter = ['created_at']
    search_fields = ['product_name', 'product_sku', 'order__id']
    readonly_fields = ['order', 'product', 'created_at']