

# # # apps/products/views.py

# # """
# # Product Views

# # Essential API views for product management.
# # Clean, well-documented, and properly validated.
# # """

# # from rest_framework import generics, status, filters
# # from rest_framework.permissions import IsAuthenticated, AllowAny
# # from rest_framework.response import Response
# # from django_filters.rest_framework import DjangoFilterBackend
# # from drf_spectacular.utils import extend_schema, OpenApiParameter
# # from drf_spectacular.types import OpenApiTypes
# # from django.db.models import Q

# # from .models import Product
# # from .serializers import (
# #     ProductListSerializer,
# #     ProductDetailSerializer,
# #     ProductCreateSerializer
# # )


# # class ProductListView(generics.ListAPIView):
# #     """
# #     API 1: Get list of products with filtering and search
    
# #     Features:
# #     - Public endpoint (no auth required)
# #     - Search by name/description
# #     - Filter by category, price range, featured status
# #     - Ordering by various fields
# #     - Only shows active products
# #     """
    
# #     serializer_class = ProductListSerializer
# #     permission_classes = [AllowAny]
# #     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
# #     search_fields = ['name', 'description', 'short_description']
# #     ordering_fields = ['name', 'price', 'created_at', 'stock_quantity']
# #     ordering = ['-created_at']  # Default: newest first
    
# #     def get_queryset(self):
# #         """Get filtered queryset with optimizations"""
# #         queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
        
# #         # Apply custom filters
# #         category = self.request.query_params.get('category')
# #         min_price = self.request.query_params.get('min_price')
# #         max_price = self.request.query_params.get('max_price')
# #         is_featured = self.request.query_params.get('is_featured')
# #         in_stock = self.request.query_params.get('in_stock')
        
# #         if category:
# #             queryset = queryset.filter(category_id=category)
        
# #         if min_price:
# #             try:
# #                 queryset = queryset.filter(price__gte=float(min_price))
# #             except (ValueError, TypeError):
# #                 pass  # Ignore invalid min_price
        
# #         if max_price:
# #             try:
# #                 queryset = queryset.filter(price__lte=float(max_price))
# #             except (ValueError, TypeError):
# #                 pass  # Ignore invalid max_price
        
# #         if is_featured and is_featured.lower() in ['true', '1']:
# #             queryset = queryset.filter(is_featured=True)
        
# #         if in_stock and in_stock.lower() in ['true', '1']:
# #             queryset = queryset.filter(stock_quantity__gt=0)
        
# #         return queryset
    
# #     @extend_schema(
# #         summary="List all products",
# #         description="Get paginated list of active products with filtering, search, and sorting capabilities",
# #         parameters=[
# #             OpenApiParameter(
# #                 name='category',
# #                 type=OpenApiTypes.UUID,
# #                 location=OpenApiParameter.QUERY,
# #                 description='Filter by category ID'
# #             ),
# #             OpenApiParameter(
# #                 name='min_price',
# #                 type=OpenApiTypes.DECIMAL,
# #                 location=OpenApiParameter.QUERY,
# #                 description='Minimum price filter'
# #             ),
# #             OpenApiParameter(
# #                 name='max_price',
# #                 type=OpenApiTypes.DECIMAL,
# #                 location=OpenApiParameter.QUERY,
# #                 description='Maximum price filter'
# #             ),
# #             OpenApiParameter(
# #                 name='is_featured',
# #                 type=OpenApiTypes.BOOL,
# #                 location=OpenApiParameter.QUERY,
# #                 description='Filter featured products only'
# #             ),
# #             OpenApiParameter(
# #                 name='in_stock',
# #                 type=OpenApiTypes.BOOL,
# #                 location=OpenApiParameter.QUERY,
# #                 description='Filter products in stock only'
# #             ),
# #             OpenApiParameter(
# #                 name='search',
# #                 type=OpenApiTypes.STR,
# #                 location=OpenApiParameter.QUERY,
# #                 description='Search in product name and description'
# #             ),
# #             OpenApiParameter(
# #                 name='ordering',
# #                 type=OpenApiTypes.STR,
# #                 location=OpenApiParameter.QUERY,
# #                 description='Order by: name, price, created_at, stock_quantity (add - for descending)'
# #             ),
# #         ],
# #         tags=['Products']
# #     )
# #     def get(self, request, *args, **kwargs):
# #         """Handle product list request"""
# #         try:
# #             response = super().get(request, *args, **kwargs)
            
# #             # Add metadata to response
# #             return Response({
# #                 'success': True,
# #                 'message': 'Products retrieved successfully',
# #                 'count': response.data.get('count', 0),
# #                 'next': response.data.get('next'),
# #                 'previous': response.data.get('previous'),
# #                 'results': response.data.get('results', [])
# #             })
            
# #         except Exception as e:
# #             return Response({
# #                 'success': False,
# #                 'message': 'Failed to retrieve products',
# #                 'error': str(e)
# #             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # class ProductDetailView(generics.RetrieveAPIView):
# #     """
# #     API 2: Get detailed information about a specific product
    
# #     Features:
# #     - Public endpoint (no auth required)
# #     - Uses SEO-friendly slug URLs
# #     - Complete product information
# #     - Only shows active products
# #     """
    
# #     serializer_class = ProductDetailSerializer
# #     permission_classes = [AllowAny]
# #     lookup_field = 'slug'
    
# #     def get_queryset(self):
# #         """Get optimized queryset"""
# #         return Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    
# #     @extend_schema(
# #         summary="Get product details",
# #         description="Retrieve detailed information about a specific product by slug",
# #         tags=['Products']
# #     )
# #     def get(self, request, *args, **kwargs):
# #         """Handle product detail request"""
# #         try:
# #             # Check if product exists
# #             slug = kwargs.get('slug')
# #             if not self.get_queryset().filter(slug=slug).exists():
# #                 return Response({
# #                     'success': False,
# #                     'message': 'Product not found',
# #                     'error': 'No active product found with this slug'
# #                 }, status=status.HTTP_404_NOT_FOUND)
            
# #             response = super().get(request, *args, **kwargs)
            
# #             return Response({
# #                 'success': True,
# #                 'message': 'Product details retrieved successfully',
# #                 'data': response.data
# #             })
            
# #         except Exception as e:
# #             return Response({
# #                 'success': False,
# #                 'message': 'Failed to retrieve product details',
# #                 'error': str(e)
# #             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # class ProductCreateView(generics.CreateAPIView):
# #     """
# #     API 3: Create a new product
    
# #     Features:
# #     - Requires authentication
# #     - Comprehensive validation
# #     - Auto-generates slug and SKU
# #     - Returns detailed product data after creation
# #     """
    
# #     serializer_class = ProductCreateSerializer
# #     permission_classes = [IsAuthenticated]
    
# #     @extend_schema(
# #         summary="Create new product",
# #         description="Create a new product with comprehensive validation (requires authentication)",
# #         request=ProductCreateSerializer,
# #         responses={201: ProductDetailSerializer},
# #         tags=['Products']
# #     )
# #     def create(self, request, *args, **kwargs):
# #         """Handle product creation with detailed validation"""
# #         try:
# #             # Validate request data
# #             serializer = self.get_serializer(data=request.data)
            
# #             if not serializer.is_valid():
# #                 return Response({
# #                     'success': False,
# #                     'message': 'Validation failed',
# #                     'errors': serializer.errors
# #                 }, status=status.HTTP_400_BAD_REQUEST)
            
# #             # Create the product
# #             product = serializer.save()
            
# #             # Return detailed product data
# #             response_serializer = ProductDetailSerializer(
# #                 product, 
# #                 context={'request': request}
# #             )
            
# #             return Response({
# #                 'success': True,
# #                 'message': 'Product created successfully',
# #                 'data': response_serializer.data
# #             }, status=status.HTTP_201_CREATED)
            
# #         except Exception as e:
# #             return Response({
# #                 'success': False,
# #                 'message': 'Failed to create product',
# #                 'error': str(e)
# #             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# # apps/products/views.py

# """
# Product Views

# Essential API views for product management.
# Clean, well-documented, and properly validated.
# """

# from rest_framework import generics, status, filters
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.response import Response
# from django_filters.rest_framework import DjangoFilterBackend
# from drf_spectacular.utils import extend_schema, OpenApiParameter
# from drf_spectacular.types import OpenApiTypes
# from django.db.models import Q

# from .models import Product
# from .serializers import (
#     ProductListSerializer,
#     ProductDetailSerializer,
#     ProductCreateSerializer
# )


# class ProductListView(generics.ListAPIView):
#     """
#     API 1: Get list of products with filtering and search
    
#     Features:
#     - Public endpoint (no auth required)
#     - Search by name/description
#     - Filter by category, price range, featured status
#     - Ordering by various fields
#     - Only shows active products
#     """
    
#     serializer_class = ProductListSerializer
#     permission_classes = [AllowAny]
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     search_fields = ['name', 'description', 'short_description']
#     ordering_fields = ['name', 'price', 'created_at', 'stock_quantity']
#     ordering = ['-created_at']  # Default: newest first
    
#     def get_queryset(self):
#         """Get filtered queryset with optimizations"""
#         queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
        
#         # Apply custom filters
#         category = self.request.query_params.get('category')
#         min_price = self.request.query_params.get('min_price')
#         max_price = self.request.query_params.get('max_price')
#         is_featured = self.request.query_params.get('is_featured')
#         in_stock = self.request.query_params.get('in_stock')
        
#         if category:
#             queryset = queryset.filter(category_id=category)
        
#         if min_price:
#             try:
#                 queryset = queryset.filter(price__gte=float(min_price))
#             except (ValueError, TypeError):
#                 pass  # Ignore invalid min_price
        
#         if max_price:
#             try:
#                 queryset = queryset.filter(price__lte=float(max_price))
#             except (ValueError, TypeError):
#                 pass  # Ignore invalid max_price
        
#         if is_featured and is_featured.lower() in ['true', '1']:
#             queryset = queryset.filter(is_featured=True)
        
#         if in_stock and in_stock.lower() in ['true', '1']:
#             queryset = queryset.filter(stock_quantity__gt=0)
        
#         return queryset
    
#     @extend_schema(
#         summary="List all products",
#         description="Get paginated list of active products with filtering, search, and sorting capabilities",
#         parameters=[
#             OpenApiParameter(
#                 name='category',
#                 type=OpenApiTypes.UUID,
#                 location=OpenApiParameter.QUERY,
#                 description='Filter by category ID'
#             ),
#             OpenApiParameter(
#                 name='min_price',
#                 type=OpenApiTypes.DECIMAL,
#                 location=OpenApiParameter.QUERY,
#                 description='Minimum price filter'
#             ),
#             OpenApiParameter(
#                 name='max_price',
#                 type=OpenApiTypes.DECIMAL,
#                 location=OpenApiParameter.QUERY,
#                 description='Maximum price filter'
#             ),
#             OpenApiParameter(
#                 name='is_featured',
#                 type=OpenApiTypes.BOOL,
#                 location=OpenApiParameter.QUERY,
#                 description='Filter featured products only'
#             ),
#             OpenApiParameter(
#                 name='in_stock',
#                 type=OpenApiTypes.BOOL,
#                 location=OpenApiParameter.QUERY,
#                 description='Filter products in stock only'
#             ),
#             OpenApiParameter(
#                 name='search',
#                 type=OpenApiTypes.STR,
#                 location=OpenApiParameter.QUERY,
#                 description='Search in product name and description'
#             ),
#             OpenApiParameter(
#                 name='ordering',
#                 type=OpenApiTypes.STR,
#                 location=OpenApiParameter.QUERY,
#                 description='Order by: name, price, created_at, stock_quantity (add - for descending)'
#             ),
#         ],
#         tags=['products']
#     )
#     def get(self, request, *args, **kwargs):
#         """Handle product list request"""
#         try:
#             response = super().get(request, *args, **kwargs)
            
#             # Add metadata to response
#             return Response({
#                 'success': True,
#                 'message': 'Products retrieved successfully',
#                 'count': response.data.get('count', 0),
#                 'next': response.data.get('next'),
#                 'previous': response.data.get('previous'),
#                 'results': response.data.get('results', [])
#             })
            
#         except Exception as e:
#             return Response({
#                 'success': False,
#                 'message': 'Failed to retrieve products',
#                 'error': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ProductDetailView(generics.RetrieveAPIView):
#     """
#     API 2: Get detailed information about a specific product
    
#     Features:
#     - Public endpoint (no auth required)
#     - Uses SEO-friendly slug URLs
#     - Complete product information
#     - Only shows active products
#     """
    
#     serializer_class = ProductDetailSerializer
#     permission_classes = [AllowAny]
#     lookup_field = 'slug'
    
#     def get_queryset(self):
#         """Get optimized queryset"""
#         return Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    
#     @extend_schema(
#         summary="Get product details",
#         description="Retrieve detailed information about a specific product by slug",
#         tags=['products']
#     )
#     def get(self, request, *args, **kwargs):
#         """Handle product detail request"""
#         try:
#             # Check if product exists
#             slug = kwargs.get('slug')
#             if not self.get_queryset().filter(slug=slug).exists():
#                 return Response({
#                     'success': False,
#                     'message': 'Product not found',
#                     'error': 'No active product found with this slug'
#                 }, status=status.HTTP_404_NOT_FOUND)
            
#             response = super().get(request, *args, **kwargs)
            
#             return Response({
#                 'success': True,
#                 'message': 'Product details retrieved successfully',
#                 'data': response.data
#             })
            
#         except Exception as e:
#             return Response({
#                 'success': False,
#                 'message': 'Failed to retrieve product details',
#                 'error': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ProductCreateView(generics.CreateAPIView):
#     """
#     API 3: Create a new product
    
#     Features:
#     - Requires authentication
#     - Comprehensive validation
#     - Auto-generates slug and SKU
#     - Returns detailed product data after creation
#     """
    
#     serializer_class = ProductCreateSerializer
#     permission_classes = [IsAuthenticated]
    
#     @extend_schema(
#         summary="Create new product", 
#         description="Create a new product with comprehensive validation (requires authentication)",
#         request=ProductCreateSerializer,
#         responses={201: ProductDetailSerializer},
#         tags=['Products'],
#         operation_id='products_create'  # Add explicit operation_id
#     )
#     def create(self, request, *args, **kwargs):
#         """Handle product creation with detailed validation"""
#         try:
#             # Validate request data
#             serializer = self.get_serializer(data=request.data)
            
#             if not serializer.is_valid():
#                 return Response({
#                     'success': False,
#                     'message': 'Validation failed',
#                     'errors': serializer.errors
#                 }, status=status.HTTP_400_BAD_REQUEST)
            
#             # Create the product
#             product = serializer.save()
            
#             # Return detailed product data
#             response_serializer = ProductDetailSerializer(
#                 product, 
#                 context={'request': request}
#             )
            
#             return Response({
#                 'success': True,
#                 'message': 'Product created successfully',
#                 'data': response_serializer.data
#             }, status=status.HTTP_201_CREATED)
            
#         except Exception as e:
#             return Response({
#                 'success': False,
#                 'message': 'Failed to create product',
#                 'error': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# apps/products/views.py

"""
Product Views

Essential API views for product management.
Clean, well-documented, and properly validated.
"""

from rest_framework import generics, status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q
from apps.authentication.permissions import IsAdminUser

from .models import Product
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateSerializer
)


class ProductListView(generics.ListAPIView):
    """
    API 1: Get list of products with filtering and search
    
    Features:
    - Public endpoint (no auth required)
    - Search by name/description
    - Filter by category, price range, featured status
    - Ordering by various fields
    - Only shows active products
    """
    
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'short_description']
    ordering_fields = ['name', 'price', 'created_at', 'stock_quantity']
    ordering = ['-created_at']  # Default: newest first
    
    def get_queryset(self):
        """Get filtered queryset with optimizations"""
        queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
        
        # Apply custom filters
        category = self.request.query_params.get('category')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        is_featured = self.request.query_params.get('is_featured')
        in_stock = self.request.query_params.get('in_stock')
        
        if category:
            queryset = queryset.filter(category_id=category)
        
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except (ValueError, TypeError):
                pass  # Ignore invalid min_price
        
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except (ValueError, TypeError):
                pass  # Ignore invalid max_price
        
        if is_featured and is_featured.lower() in ['true', '1']:
            queryset = queryset.filter(is_featured=True)
        
        if in_stock and in_stock.lower() in ['true', '1']:
            queryset = queryset.filter(stock_quantity__gt=0)
        
        return queryset
    
    @extend_schema(
        summary="List all products",
        description="Get paginated list of active products with filtering, search, and sorting capabilities",
        parameters=[
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                description='Filter by category ID'
            ),
            OpenApiParameter(
                name='min_price',
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description='Minimum price filter'
            ),
            OpenApiParameter(
                name='max_price',
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description='Maximum price filter'
            ),
            OpenApiParameter(
                name='is_featured',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter featured products only'
            ),
            OpenApiParameter(
                name='in_stock',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter products in stock only'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search in product name and description'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Order by: name, price, created_at, stock_quantity (add - for descending)'
            ),
        ],
        tags=['products']
    )
    def get(self, request, *args, **kwargs):
        """Handle product list request"""
        try:
            response = super().get(request, *args, **kwargs)
            
            # Add metadata to response
            return Response({
                'success': True,
                'message': 'Products retrieved successfully',
                'count': response.data.get('count', 0),
                'next': response.data.get('next'),
                'previous': response.data.get('previous'),
                'results': response.data.get('results', [])
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to retrieve products',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductDetailView(generics.RetrieveAPIView):
    """
    API 2: Get detailed information about a specific product
    
    Features:
    - Public endpoint (no auth required)
    - Uses SEO-friendly slug URLs
    - Complete product information
    - Only shows active products
    """
    
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Get optimized queryset"""
        return Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    
    @extend_schema(
        summary="Get product details",
        description="Retrieve detailed information about a specific product by slug",
        tags=['products']
    )
    def get(self, request, *args, **kwargs):
        """Handle product detail request"""
        try:
            # Check if product exists
            slug = kwargs.get('slug')
            if not self.get_queryset().filter(slug=slug).exists():
                return Response({
                    'success': False,
                    'message': 'Product not found',
                    'error': 'No active product found with this slug'
                }, status=status.HTTP_404_NOT_FOUND)
            
            response = super().get(request, *args, **kwargs)
            
            return Response({
                'success': True,
                'message': 'Product details retrieved successfully',
                'data': response.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to retrieve product details',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductCreateView(generics.CreateAPIView):
    """
    API 3: Create a new product
    
    Features:
    - Requires authentication
    - Comprehensive validation
    - Auto-generates slug and SKU
    - Returns detailed product data after creation
    """
    
    serializer_class = ProductCreateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        summary="Create new product", 
        description="Create a new product with comprehensive validation (requires authentication)",
        request=ProductCreateSerializer,
        responses={201: ProductDetailSerializer},
        tags=['Products'],
        operation_id='Products_create'  # Add explicit operation_id
    )
    def create(self, request, *args, **kwargs):
        """Handle product creation with detailed validation"""
        try:
            # Validate request data
            serializer = self.get_serializer(data=request.data)
            
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the product
            product = serializer.save()
            
            # Return detailed product data
            response_serializer = ProductDetailSerializer(
                product, 
                context={'request': request}
            )
            
            return Response({
                'success': True,
                'message': 'Product created successfully',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to create product',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)