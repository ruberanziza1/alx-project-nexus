# apps/orders/serializers.py

"""
Order Serializers

Serializers for order operations.
"""

from rest_framework import serializers
from decimal import Decimal
from .models import Order, OrderItem
from apps.carts.models import Cart, CartItem


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for Order Item display"""
    
    product_id = serializers.UUIDField(source='product.id', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product_id',
            'product_name',
            'product_sku',
            'product_slug',
            'quantity',
            'unit_price',
            'subtotal',
            'created_at'
        ]


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for Order list view"""
    
    total_items = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'status_display',
            'total_items',
            'total_amount',
            'created_at',
            'updated_at'
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    """Serializer for Order detail view"""
    
    items = OrderItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id',
            'user_email',
            'status',
            'status_display',
            'subtotal',
            'total_amount',
            'total_items',
            'shipping_address',
            'shipping_city',
            'shipping_country',
            'shipping_postal_code',
            'order_notes',
            'items',
            'created_at',
            'updated_at'
        ]


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating order from cart"""
    
    # Optional shipping information
    shipping_address = serializers.CharField(required=False, allow_blank=True, max_length=500)
    shipping_city = serializers.CharField(required=False, allow_blank=True, max_length=100)
    shipping_country = serializers.CharField(required=False, allow_blank=True, max_length=100)
    shipping_postal_code = serializers.CharField(required=False, allow_blank=True, max_length=20)
    order_notes = serializers.CharField(required=False, allow_blank=True, max_length=1000)
    
    def validate(self, attrs):
        """Validate cart has items and stock availability"""
        user = self.context['request'].user
        
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart is empty. Add items before placing order.")
        
        if not cart.items.exists():
            raise serializers.ValidationError("Cart is empty. Add items before placing order.")
        
        # Validate stock availability for all items
        for cart_item in cart.items.all():
            if not cart_item.is_available:
                raise serializers.ValidationError({
                    'cart': f"Product '{cart_item.product.name}' is no longer available."
                })
            
            if cart_item.product.stock_quantity < cart_item.quantity:
                raise serializers.ValidationError({
                    'cart': f"Insufficient stock for '{cart_item.product.name}'. Only {cart_item.product.stock_quantity} available."
                })
        
        attrs['cart'] = cart
        return attrs
    
    def create(self, validated_data):
        """Create order from cart"""
        cart = validated_data.pop('cart')
        user = self.context['request'].user
        
        # Calculate totals
        subtotal = cart.total_price
        total_amount = subtotal  # Add shipping/tax later if needed
        
        # Create order
        order = Order.objects.create(
            user=user,
            subtotal=subtotal,
            total_amount=total_amount,
            shipping_address=validated_data.get('shipping_address', ''),
            shipping_city=validated_data.get('shipping_city', ''),
            shipping_country=validated_data.get('shipping_country', ''),
            shipping_postal_code=validated_data.get('shipping_postal_code', ''),
            order_notes=validated_data.get('order_notes', '')
        )
        
        # Create order items from cart items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                subtotal=cart_item.subtotal
            )
            
            # Reduce product stock
            cart_item.product.stock_quantity -= cart_item.quantity
            cart_item.product.save()
        
        # Clear cart after order is created
        cart.items.all().delete()
        
        return order


class UpdateOrderStatusSerializer(serializers.ModelSerializer):
    """Serializer for updating order status (Admin only)"""
    
    class Meta:
        model = Order
        fields = ['status']
    
    def validate_status(self, value):
        """Validate status transition"""
        instance = self.instance
        
        # Define valid status transitions
        valid_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled'],
            'delivered': [],  # Final state
            'cancelled': []   # Final state
        }
        
        if instance and instance.status in ['delivered', 'cancelled']:
            raise serializers.ValidationError(
                f"Cannot change status from '{instance.get_status_display()}'"
            )
        
        if instance and value not in valid_transitions.get(instance.status, []):
            raise serializers.ValidationError(
                f"Cannot change status from '{instance.get_status_display()}' to '{value}'"
            )
        
        return value