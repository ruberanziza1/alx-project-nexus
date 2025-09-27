
# apps/products/views.py

"""
Simple Product Views - Products Only, No Category APIs

Category is just a text field in products.
"""

from rest_framework import generics, filters,  status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiExample

from .permissions import IsAdminUser
from .models import Product
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer
)
from .filters import ProductFilter
from rest_framework.response import Response
from .pagination import ProductPagination


class ProductListCreateView(generics.ListCreateAPIView):
    """
    List all products with filtering and search OR Create new product with images
    """
    
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'sku', 'category']
    ordering_fields = ['name', 'price', 'created_at', 'category']
    ordering = ['-created_at']
    pagination_class = ProductPagination
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateUpdateSerializer
        return ProductListSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]
    
    def get_queryset(self):
        if self.request.method == 'GET':
            return Product.objects.filter(is_active=True)
        return Product.objects.all()

    @extend_schema(
        summary="List all products",
        description="""
        Get paginated list of products. 
        
        **Filters:**
        - category: Filter by category name (e.g., ?category=Electronics)
        - price: Filter by price range
        - search: Search by name, description, SKU, or category
        
        **Public access.**
        """,
        tags=['Products']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create new product with images",
        description="""
        Create a new product with images and category. 
        
        **Content-Type: multipart/form-data**
        
        **Fields:**
        - name: Product name (required)
        - description: Product description (required)
        - price: Product price (required)
        - category: Category name (required) - e.g., "Electronics", "Books"
        - stock_quantity: Stock quantity (required)
        - images: Product images (optional, max 5 files)
        
        **Category is just text - no need to create category separately!**
        
        Requires admin authentication.
        """,
        tags=['Products'],
        examples=[
            OpenApiExample(
                'Create Product',
                value={
                    'name': 'Gaming Laptop',
                    'description': 'High performance gaming laptop with RTX 4080',
                    'short_description': 'Best gaming laptop',
                    'price': '1299.99',
                    'compare_price': '1499.99',
                    'stock_quantity': 25,
                    'low_stock_threshold': 5,
                    'category': 'Electronics',
                    'is_featured': True,
                    'images': 'Upload files here (multiple allowed)'
                },
                request_only=True
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ProductDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get product details OR Update product OR Delete product
    """
    
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    lookup_field = 'pk'
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductDetailSerializer
        return ProductCreateUpdateSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]
    
    def get_queryset(self):
        if self.request.method == 'GET':
            return Product.objects.filter(is_active=True)
        return Product.objects.all()
    
    def get_object(self):
        lookup_value = self.kwargs.get('pk')
        
        # Try UUID first, then slug
        try:
            if len(lookup_value) == 36 and '-' in lookup_value:
                return get_object_or_404(self.get_queryset(), id=lookup_value)
            else:
                return get_object_or_404(self.get_queryset(), slug=lookup_value)
        except Exception as e:
            # If both UUID and slug fail, raise 404
            from django.http import Http404
            raise Http404(f"Product with id/slug '{lookup_value}' not found")

    @extend_schema(
        summary="Get product details",
        description="Retrieve complete product information including images, category, pricing, and stock details. Use product ID or slug.",
        tags=['Products']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update product with images",
        description="""
        Update product information including category and adding new images.
        
        **Content-Type: multipart/form-data**
        
        You can update category by just providing new category name.
        New images will be appended to existing ones.
        
        Requires admin authentication.
        """,
        tags=['Products']
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Partial update product",
        description="""
        Update specific product fields including category.
        
        **Content-Type: multipart/form-data**
        
        Send only the fields you want to update.
        
        Requires admin authentication.
        """,
        tags=['Products']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Delete product",
        description="Soft delete product (sets is_active=False). Product will be hidden from public listings. Requires admin authentication.",
        tags=['Products']
    )
    def delete(self, request, *args, **kwargs):
     instance = self.get_object()
     product_name = instance.name
     instance.delete()  # Permanent deletion from database
     return Response(
        {"message": f"Product '{product_name}' permanently deleted"}, 
        status=status.HTTP_200_OK
    )