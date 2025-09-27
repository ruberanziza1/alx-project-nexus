

# apps/products/urls.py

"""
Products URL Configuration - Simple & Clean

Only product endpoints, no category APIs needed!
"""

from django.urls import path
from .views import (
    ProductListCreateView,
    ProductDetailUpdateDeleteView,
)

app_name = 'products'

urlpatterns = [
    # Product List & Create
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    
    # Individual product endpoint
    path('<str:pk>/', ProductDetailUpdateDeleteView.as_view(), name='product-detail-update-delete'),
]

# ========================================================================
# COMPLETE API ENDPOINTS
# ========================================================================
"""
PRODUCTS ENDPOINTS:
- GET    /api/v1/products/           → List all products with filtering
- POST   /api/v1/products/           → Create new product (Admin only)
- GET    /api/v1/products/{id}/      → Get product details  
- PUT    /api/v1/products/{id}/      → Full update product (Admin only)
- PATCH  /api/v1/products/{id}/      → Partial update product (Admin only)
- DELETE /api/v1/products/{id}/      → Delete product (Admin only)

EXAMPLE REQUESTS:

1. List all products:
   GET /api/v1/products/

2. Filter by category:
   GET /api/v1/products/?category=Electronics

3. Search products:
   GET /api/v1/products/?search=laptop

4. Create product:
   POST /api/v1/products/
   {
     "name": "Gaming Laptop",
     "description": "High performance laptop",
     "price": 1299.99,
     "category": "Electronics",
     "stock_quantity": 50
   }

5. Update product category:
   PATCH /api/v1/products/{id}/
   {
     "category": "Gaming"
   }

6. Get product by slug:
   GET /api/v1/products/gaming-laptop/
"""