# apps/carts/serializers.py

"""
Cart Serializers

Serializers for cart and cart item operations.
"""

from rest_framework import serializers
from decimal import Decimal
from .models import Cart, CartItem
from apps.products.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for Cart Item display"""
    
    # Product information
    product_id = serializers.UUIDField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    product_image = serializers.SerializerMethodField()
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    
    # Pricing information
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    compare_unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    compare_subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    # Availability
    is_available = serializers.BooleanField(read_only=True)
    stock_available = serializers.IntegerField(source='product.stock_quantity', read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'id',
            'product_id',
            'product_name',
            'product_slug',
            'product_image',
            'product_sku',
            'quantity',
            'unit_price',
            'compare_unit_price',
            'subtotal',
            'compare_subtotal',
            'savings',
            'is_available',
            'stock_available',
            'created_at',
            'updated_at'
        ]
    
    def get_product_image(self, obj):
        """Get primary product image URL"""
        primary_image = obj.product.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        return None


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart display"""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_compare_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_savings = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            'id',
            'items',
            'total_items',
            'total_price',
            'total_compare_price',
            'total_savings',
            'created_at',
            'updated_at'
        ]


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart"""
    
    product_id = serializers.UUIDField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1, max_value=999)
    
    def validate_product_id(self, value):
        """Validate product exists and is active"""
        try:
            product = Product.objects.get(id=value, is_active=True)
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or is not active.")
    
    def validate_quantity(self, value):
        """Validate quantity is reasonable"""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        
        if value > 999:
            raise serializers.ValidationError("Quantity cannot exceed 999.")
        
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        product_id = attrs.get('product_id')
        quantity = attrs.get('quantity')
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            
            # Check stock availability
            if product.stock_quantity < quantity:
                raise serializers.ValidationError({
                    'quantity': f'Only {product.stock_quantity} items available in stock.'
                })
            
            # Store product for use in view
            attrs['product'] = product
            
        except Product.DoesNotExist:
            raise serializers.ValidationError({
                'product_id': 'Product not found or is not active.'
            })
        
        return attrs


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity"""
    
    quantity = serializers.IntegerField(required=True, min_value=1, max_value=999)
    
    def validate_quantity(self, value):
        """Validate quantity"""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        
        if value > 999:
            raise serializers.ValidationError("Quantity cannot exceed 999.")
        
        return value
    
    def validate(self, attrs):
        """Validate stock availability"""
        quantity = attrs.get('quantity')
        cart_item = self.context.get('cart_item')
        
        if cart_item and cart_item.product.stock_quantity < quantity:
            raise serializers.ValidationError({
                'quantity': f'Only {cart_item.product.stock_quantity} items available in stock.'
            })
        
        return attrs