# apps/payments/serializers.py

"""
Payment Serializers for Stripe Integration
"""

from rest_framework import serializers
from .models import Payment
from apps.orders.models import Order


class CreateCheckoutSessionSerializer(serializers.Serializer):
    """Serializer for creating Stripe checkout session"""
    
    order_id = serializers.UUIDField(required=True)
    
    def validate_order_id(self, value):
        """Validate order exists and belongs to user"""
        user = self.context['request'].user
        
        try:
            order = Order.objects.get(id=value, user=user)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found or does not belong to you.")
        
        # Check if order is pending
        if order.status != 'pending':
            raise serializers.ValidationError(f"Cannot pay for order with status: {order.get_status_display()}")
        
        # Check if already paid
        if hasattr(order, 'payment') and order.payment.status == 'paid':
            raise serializers.ValidationError("Order is already paid.")
        
        return value


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment display"""
    
    order_id = serializers.UUIDField(source='order.id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id',
            'order_id',
            'amount',
            'currency',
            'status',
            'status_display',
            'payment_method',
            'payment_method_display',
            'transaction_id',
            'payment_date',
            'failure_reason',
            'created_at',
            'updated_at'
        ]


class PaymentDetailSerializer(serializers.ModelSerializer):
    """Detailed Payment Serializer with order info"""
    
    order_id = serializers.UUIDField(source='order.id', read_only=True)
    order_status = serializers.CharField(source='order.status', read_only=True)
    order_total = serializers.DecimalField(source='order.total_amount', max_digits=10, decimal_places=2, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id',
            'order_id',
            'order_status',
            'order_total',
            'amount',
            'currency',
            'status',
            'status_display',
            'payment_method',
            'transaction_id',
            'stripe_payment_intent_id',
            'payment_date',
            'failure_reason',
            'created_at',
            'updated_at'
        ]