# # apps/carts/urls.py

# """
# Cart URL Configuration

# Complete URL patterns for cart operations.
# All endpoints require user authentication.
# """

# from django.urls import path
# from .views import (
#     CartView,
#     AddToCartView,
#     UpdateCartItemView,
#     RemoveFromCartView,
#     ClearCartView,
# )

# app_name = 'carts'

# urlpatterns = [
#     # ========================================================================
#     # CART ENDPOINTS
#     # ========================================================================
    
#     # Cart operations
#     path('', CartView.as_view(), name='cart-view'),                    # GET /api/v1/carts/
#     path('add/', AddToCartView.as_view(), name='cart-add'),            # POST /api/v1/carts/add/
#     path('clear/', ClearCartView.as_view(), name='cart-clear'),        # DELETE /api/v1/carts/clear/
    
#     # Cart item operations
#     path('update/<uuid:pk>/', UpdateCartItemView.as_view(), name='cart-update'),  # PUT /api/v1/carts/update/{item_id}/
#     path('remove/<uuid:pk>/', RemoveFromCartView.as_view(), name='cart-remove'),  # DELETE /api/v1/carts/remove/{item_id}/
# ]

# # ========================================================================
# # COMPLETE CART API ENDPOINTS STRUCTURE
# # ========================================================================
# """
# CART ENDPOINTS (All require authentication):

# Main Cart Operations:
# - GET    /api/v1/carts/           → View current user's cart
# - POST   /api/v1/carts/add/       → Add product to cart
# - DELETE /api/v1/carts/clear/     → Clear entire cart

# Cart Item Operations:
# - PUT    /api/v1/carts/update/{item_id}/  → Update item quantity
# - DELETE /api/v1/carts/remove/{item_id}/  → Remove specific item

# EXAMPLE REQUESTS:

# 1. View cart:
#    GET /api/v1/carts/
#    Headers: Authorization: Token your_token

# 2. Add product to cart:
#    POST /api/v1/carts/add/
#    Headers: Authorization: Token your_token
#    Body: {
#      "product_id": "123e4567-e89b-12d3-a456-426614174000",
#      "quantity": 2
#    }

# 3. Update cart item quantity:
#    PUT /api/v1/carts/update/456e7890-e89b-12d3-a456-426614174000/
#    Headers: Authorization: Token your_token
#    Body: {
#      "quantity": 3
#    }

# 4. Remove item from cart:
#    DELETE /api/v1/carts/remove/456e7890-e89b-12d3-a456-426614174000/
#    Headers: Authorization: Token your_token

# 5. Clear entire cart:
#    DELETE /api/v1/carts/clear/
#    Headers: Authorization: Token your_token

# TYPICAL CART WORKFLOW:
# 1. User adds products → POST /carts/add/
# 2. User views cart → GET /carts/
# 3. User updates quantities → PUT /carts/update/{item_id}/
# 4. User removes items → DELETE /carts/remove/{item_id}/
# 5. User proceeds to checkout (future feature)
# 6. Or user clears cart → DELETE /carts/clear/
# """



# apps/carts/urls.py

"""
Cart URL Configuration - Consolidated

Consolidated URL patterns for cart operations.
All endpoints require user authentication.
"""

from django.urls import path
from .views import (
    CartView,
    CartItemView,
)

app_name = 'carts'

urlpatterns = [
    # ========================================================================
    # CONSOLIDATED CART ENDPOINTS
    # ========================================================================
    
    # Main cart endpoint - handles GET, POST (add), DELETE (clear)
    path('', CartView.as_view(), name='cart-operations'),
    
    # Individual cart item endpoint - handles PUT, PATCH, DELETE
    path('<uuid:item_id>/', CartItemView.as_view(), name='cart-item-operations'),
]

# ========================================================================
# COMPLETE CART API ENDPOINTS STRUCTURE (CONSOLIDATED)
# ========================================================================
"""
Now your cart APIs will appear on the same lines like products:

ENDPOINT: /api/v1/carts/
├── GET     → View current user's cart
├── POST    → Add product to cart  
└── DELETE  → Clear entire cart

ENDPOINT: /api/v1/carts/{item_id}/
├── PUT     → Update item quantity
├── PATCH   → Partial update item quantity
└── DELETE  → Remove specific item from cart

EXAMPLE REQUESTS:

1. View cart:
   GET /api/v1/carts/

2. Add to cart:
   POST /api/v1/carts/
   {
     "product_id": "123e4567-e89b-12d3-a456-426614174000",
     "quantity": 2
   }

3. Clear cart:
   DELETE /api/v1/carts/

4. Update item quantity:
   PUT /api/v1/carts/456e7890-e89b-12d3-a456-426614174000/
   {
     "quantity": 5
   }

5. Remove item:
   DELETE /api/v1/carts/456e7890-e89b-12d3-a456-426614174000/

CLEAN API STRUCTURE - CONSOLIDATED LIKE PRODUCTS! 🎯
"""