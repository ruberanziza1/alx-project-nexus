# apps/payments/urls.py

"""
Payments URL Configuration
"""

from django.urls import path
from .views import (
    CreateCheckoutSessionView,
    CheckSessionStatusView,
    StripeWebhookView,
    OrderPaymentDetailView
)

app_name = 'payments'

urlpatterns = [
    # Create checkout session
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout'),
    
    # Check session status
    path('session-status/<str:session_id>/', CheckSessionStatusView.as_view(), name='session-status'),
    
    # Stripe webhook
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    
    # Get payment for order
    path('order/<uuid:order_id>/', OrderPaymentDetailView.as_view(), name='order-payment'),
]

# ========================================================================
# PAYMENT API ENDPOINTS
# ========================================================================
"""
PAYMENT ENDPOINTS:
- POST   /api/v1/payments/create-checkout-session/   → Create Stripe checkout
- GET    /api/v1/payments/session-status/{id}/       → Check payment status
- POST   /api/v1/payments/webhook/                   → Stripe webhook (automatic)
- GET    /api/v1/payments/order/{order_id}/          → Get payment for order

EXAMPLE REQUESTS:

1. Create checkout session:
   POST /api/v1/payments/create-checkout-session/
   {
     "order_id": "order-uuid-here"
   }
   
   Response:
   {
     "checkout_url": "https://checkout.stripe.com/pay/cs_test_...",
     "session_id": "cs_test_...",
     "order_id": "order-uuid"
   }

2. Check session status:
   GET /api/v1/payments/session-status/cs_test_abc123/
   
   Response:
   {
     "order_id": "order-uuid",
     "status": "paid",
     "amount": "1200.00",
     "payment_date": "2025-09-25T14:30:00Z"
   }

3. Get payment for order:
   GET /api/v1/payments/order/{order-uuid}/
   
   Response:
   {
     "id": "payment-uuid",
     "order_id": "order-uuid",
     "status": "paid",
     "amount": "1200.00",
     "transaction_id": "pi_..."
   }
"""