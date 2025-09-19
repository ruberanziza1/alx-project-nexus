# apps/products/urls.py

"""
Products URL Configuration

Defines essential URL patterns for product endpoints.
Clean and consistent URL structure.
"""

from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    ProductCreateView,
)

app_name = 'products'

urlpatterns = [
    # ========================================================================
    # PRODUCT ENDPOINTS
    # ========================================================================
    
    # Product operations - all on same level
    # Note: 'products/' prefix is already in main urls.py, so we don't repeat it here
    path('', ProductListView.as_view(), name='product-list'),                    # /api/v1/products/
    path('create/', ProductCreateView.as_view(), name='product-create'),         # /api/v1/products/create/
    path('<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),    # /api/v1/products/{slug}/
]