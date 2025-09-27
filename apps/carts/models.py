# apps/carts/models.py

"""
Cart Models

Shopping cart and cart item models for e-commerce functionality.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.core.validators import MinValueValidator

User = get_user_model()


class Cart(models.Model):
    """
    Shopping Cart Model
    Each user can have one active cart
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='cart',
        help_text="Each user has one cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Carts'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    @property
    def total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        """Calculate total price of all items in cart"""
        total = Decimal('0.00')
        for item in self.items.select_related('product'):
            total += item.subtotal
        return total
    
    @property
    def total_compare_price(self):
        """Calculate total compare price (original prices) of all items"""
        total = Decimal('0.00')
        for item in self.items.select_related('product'):
            compare_price = item.product.compare_price or item.product.price
            total += compare_price * item.quantity
        return total
    
    @property
    def total_savings(self):
        """Calculate total savings from discounts"""
        return self.total_compare_price - self.total_price
    
    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()
        self.save()


class CartItem(models.Model):
    """
    Cart Item Model
    Represents a product in the shopping cart
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.CASCADE,
        help_text="Product in the cart"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantity of this product in cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'product']  # One product per cart
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cart', 'product']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.cart.user.username}'s cart"
    
    @property
    def unit_price(self):
        """Get the current price of the product"""
        return self.product.price
    
    @property
    def compare_unit_price(self):
        """Get the compare price of the product"""
        return self.product.compare_price or self.product.price
    
    @property
    def subtotal(self):
        """Calculate subtotal for this cart item"""
        return self.unit_price * self.quantity
    
    @property
    def compare_subtotal(self):
        """Calculate compare subtotal (original price) for this cart item"""
        return self.compare_unit_price * self.quantity
    
    @property
    def savings(self):
        """Calculate savings from discount on this item"""
        return self.compare_subtotal - self.subtotal
    
    @property
    def is_available(self):
        """Check if product is available in requested quantity"""
        return (
            self.product.is_active and 
            self.product.stock_quantity >= self.quantity
        )
    
    def save(self, *args, **kwargs):
        """Override save to update cart's updated_at timestamp"""
        super().save(*args, **kwargs)
        # Update cart's timestamp when item is modified
        self.cart.save(update_fields=['updated_at'])
    
    def delete(self, *args, **kwargs):
        """Override delete to update cart's updated_at timestamp"""
        cart = self.cart
        super().delete(*args, **kwargs)
        # Update cart's timestamp when item is deleted
        cart.save(update_fields=['updated_at'])