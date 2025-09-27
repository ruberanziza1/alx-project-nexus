# apps/orders/urls.py

"""
Orders URL Configuration
"""

from django.urls import path
from .views import (
    OrderListCreateView,
    OrderDetailView,
    OrderUpdateStatusView,
    OrderCancelView
)

app_name = 'orders'

urlpatterns = [
    # Order List & Create
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    
    # Order Detail
    path('<uuid:pk>/', OrderDetailView.as_view(), name='order-detail'),
    
    # Update Order Status (Admin)
    path('<uuid:pk>/status/', OrderUpdateStatusView.as_view(), name='order-update-status'),
    
    # Cancel Order (User)
    path('<uuid:pk>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
]

# ========================================================================
# ORDER API ENDPOINTS
# ========================================================================
"""
ORDERS ENDPOINTS:
- POST   /api/v1/orders/                → Create order from cart
- GET    /api/v1/orders/                → List user's orders
- GET    /api/v1/orders/{id}/           → Get order details
- PATCH  /api/v1/orders/{id}/status/    → Update order status (Admin only)
- PATCH  /api/v1/orders/{id}/cancel/    → Cancel order (User)

EXAMPLE REQUESTS:

1. Create order from cart:
   POST /api/v1/orders/
   {
     "shipping_address": "123 Main St",
     "shipping_city": "New York",
     "shipping_country": "USA",
     "shipping_postal_code": "10001",
     "order_notes": "Please deliver in the morning"
   }

2. List user's orders:
   GET /api/v1/orders/

3. Get order details:
   GET /api/v1/orders/{order-id}/

4. Update order status (Admin):
   PATCH /api/v1/orders/{order-id}/status/
   {
     "status": "shipped"
   }

5. Cancel order (User):
   PATCH /api/v1/orders/{order-id}/cancel/
"""