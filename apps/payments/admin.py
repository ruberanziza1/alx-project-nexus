# apps/payments/admin.py

"""
Payment Admin Configuration
"""

from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin for Payment model"""
    
    list_display = [
        'id',
        'order',
        'amount',
        'status',
        'payment_method',
        'payment_date',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'payment_method',
        'created_at',
        'payment_date'
    ]
    
    search_fields = [
        'order__id',
        'transaction_id',
        'stripe_checkout_session_id',
        'stripe_payment_intent_id'
    ]
    
    readonly_fields = [
        'id',
        'order',
        'stripe_checkout_session_id',
        'stripe_payment_intent_id',
        'transaction_id',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('id', 'order', 'amount', 'currency', 'status', 'payment_method')
        }),
        ('Stripe Details', {
            'fields': ('stripe_checkout_session_id', 'stripe_payment_intent_id', 'transaction_id')
        }),
        ('Additional Info', {
            'fields': ('payment_date', 'failure_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )