

# apps/products/serializers.py

"""
Simple Product Serializers - Category as text field

No category table, no category APIs needed!
"""

from rest_framework import serializers
from decimal import Decimal
from .models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for Product Images"""
    
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'is_primary', 'order']
    
    def get_image_url(self, obj):
        """Get full image URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for Product list view"""
    
    primary_image = serializers.SerializerMethodField(read_only=True)
    stock_status = serializers.CharField(read_only=True)
    discount_percentage = serializers.FloatField(read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'short_description',
            'price',
            'compare_price',
            'sku',
            'stock_quantity',
            'category',
            'primary_image',
            'stock_status',
            'discount_percentage',
            'is_on_sale',
            'is_featured',
            'is_active',
            'created_at'
        ]
    
    def get_primary_image(self, obj):
        """Get primary image URL"""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for Product detail view"""
    
    images = ProductImageSerializer(many=True, read_only=True)
    stock_status = serializers.CharField(read_only=True)
    discount_percentage = serializers.FloatField(read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'short_description',
            'price',
            'compare_price',
            'sku',
            'stock_quantity',
            'low_stock_threshold',
            'stock_status',
            'category',
            'images',
            'is_active',
            'is_featured',
            'discount_percentage',
            'is_on_sale',
            'meta_title',
            'meta_description',
            'created_at',
            'updated_at'
        ]


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Simple Product Serializer - Category as text field
    
    Example: {"name": "Laptop", "category": "Electronics", "price": 1200}
    """
    
    # Image upload fields
    images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'short_description',
            'price',
            'compare_price',
            'stock_quantity',
            'low_stock_threshold',
            'category',  # Simple text field!
            'images',
            'is_active',
            'is_featured',
            'meta_title',
            'meta_description'
        ]
    
    def validate_name(self, value):
        """Validate product name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Product name is required.")
        
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Product name must be at least 3 characters long.")
        
        if len(value) > 200:
            raise serializers.ValidationError("Product name cannot exceed 200 characters.")
        
        queryset = Product.objects.filter(name__iexact=value.strip())
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        
        if queryset.exists():
            raise serializers.ValidationError("A product with this name already exists.")
        
        return value.strip()
    
    def validate_description(self, value):
        """Validate product description"""
        if not value or not value.strip():
            raise serializers.ValidationError("Product description is required.")
        
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Product description must be at least 10 characters long.")
        
        return value.strip()
    
    def validate_short_description(self, value):
        """Validate short description"""
        if value and len(value) > 300:
            raise serializers.ValidationError("Short description cannot exceed 300 characters.")
        
        return value.strip() if value else ""
    
    def validate_category(self, value):
        """Validate category"""
        if not value or not value.strip():
            raise serializers.ValidationError("Category is required.")
        
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Category must be at least 2 characters long.")
        
        if len(value) > 100:
            raise serializers.ValidationError("Category cannot exceed 100 characters.")
        
        return value.strip().title()  # Convert to Title Case (Electronics, Books, etc.)
    
    def validate_price(self, value):
        """Validate product price"""
        if value is None:
            raise serializers.ValidationError("Price is required.")
        
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        
        if value > Decimal('999999.99'):
            raise serializers.ValidationError("Price cannot exceed 999,999.99.")
        
        if value.as_tuple().exponent < -2:
            raise serializers.ValidationError("Price can have maximum 2 decimal places.")
        
        return value
    
    def validate_compare_price(self, value):
        """Validate compare price"""
        if value is not None:
            if value <= 0:
                raise serializers.ValidationError("Compare price must be greater than zero.")
            
            if value > Decimal('999999.99'):
                raise serializers.ValidationError("Compare price cannot exceed 999,999.99.")
            
            if value.as_tuple().exponent < -2:
                raise serializers.ValidationError("Compare price can have maximum 2 decimal places.")
        
        return value
    
    def validate_stock_quantity(self, value):
        """Validate stock quantity"""
        if value is None:
            raise serializers.ValidationError("Stock quantity is required.")
        
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        
        if value > 999999:
            raise serializers.ValidationError("Stock quantity cannot exceed 999,999.")
        
        return value
    
    def validate_low_stock_threshold(self, value):
        """Validate low stock threshold"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Low stock threshold cannot be negative.")
        
        return value or 10
    
    def validate_images(self, value):
        """Validate uploaded images"""
        if value:
            if len(value) > 5:
                raise serializers.ValidationError("Maximum 5 images allowed per product.")
            
            for image in value:
                if image.size > 5 * 1024 * 1024:
                    raise serializers.ValidationError(f"Image {image.name} size cannot exceed 5MB.")
                
                allowed_extensions = ['jpg', 'jpeg', 'png', 'webp']
                ext = image.name.split('.')[-1].lower()
                if ext not in allowed_extensions:
                    raise serializers.ValidationError(
                        f"Image {image.name} has invalid format. Allowed: jpg, jpeg, png, webp"
                    )
        
        return value
    
    def validate_meta_title(self, value):
        """Validate meta title"""
        if value and len(value) > 60:
            raise serializers.ValidationError("Meta title cannot exceed 60 characters.")
        
        return value.strip() if value else ""
    
    def validate_meta_description(self, value):
        """Validate meta description"""
        if value and len(value) > 160:
            raise serializers.ValidationError("Meta description cannot exceed 160 characters.")
        
        return value.strip() if value else ""
    
    def validate(self, attrs):
        """Cross-field validation"""
        price = attrs.get('price')
        compare_price = attrs.get('compare_price')
        stock_quantity = attrs.get('stock_quantity')
        low_stock_threshold = attrs.get('low_stock_threshold')
        
        if compare_price and price and compare_price <= price:
            raise serializers.ValidationError({
                'compare_price': 'Compare price must be greater than the selling price.'
            })
        
        if low_stock_threshold and stock_quantity and low_stock_threshold > stock_quantity:
            raise serializers.ValidationError({
                'low_stock_threshold': 'Low stock threshold cannot be greater than current stock quantity.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Create product with images"""
        images_data = validated_data.pop('images', [])
        
        product = Product.objects.create(**validated_data)
        
        # Create product images
        for index, image in enumerate(images_data):
            ProductImage.objects.create(
                product=product,
                image=image,
                alt_text=f"{product.name} - Image {index + 1}",
                is_primary=(index == 0),
                order=index
            )
        
        return product
    
    def update(self, instance, validated_data):
        """Update product with images"""
        images_data = validated_data.pop('images', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # Handle new images
        if images_data:
            max_order = instance.images.count()
            
            for index, image in enumerate(images_data):
                is_primary = not instance.images.filter(is_primary=True).exists() and index == 0
                
                ProductImage.objects.create(
                    product=instance,
                    image=image,
                    alt_text=f"{instance.name} - Image {max_order + index + 1}",
                    is_primary=is_primary,
                    order=max_order + index
                )
        
        return instance