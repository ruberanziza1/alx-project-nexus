# apps/payments/views.py

"""
Payment Views with Stripe Integration
"""

import stripe
from django.conf import settings
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Payment
from .serializers import (
    CreateCheckoutSessionSerializer,
    PaymentSerializer,
    PaymentDetailSerializer
)
from apps.orders.models import Order

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    """Create Stripe Checkout Session"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Create Stripe checkout session",
        description="""
        Create a Stripe checkout session for an order.
        
        **Process:**
        1. Validates order belongs to user
        2. Creates Stripe checkout session
        3. Returns checkout URL for payment
        
        **Frontend should redirect user to checkout_url**
        
        Requires authentication.
        """,
        tags=['Payments'],
        request=CreateCheckoutSessionSerializer,
    )
    def post(self, request):
        serializer = CreateCheckoutSessionSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        order_id = serializer.validated_data['order_id']
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Create or get payment record
        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                'amount': order.total_amount,
                'currency': 'usd',
                'status': 'pending'
            }
        )
        
        try:
            # Create Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': f'Order #{str(order.id)[:8]}',
                                'description': f'{order.total_items} items',
                            },
                            'unit_amount': int(order.total_amount * 100),  # Stripe uses cents
                        },
                        'quantity': 1,
                    }
                ],
                mode='payment',
                success_url=request.build_absolute_uri('/') + 'payment-success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri('/') + 'payment-cancel',
                metadata={
                    'order_id': str(order.id),
                    'payment_id': str(payment.id),
                }
            )
            
            # Save session ID
            payment.stripe_checkout_session_id = checkout_session.id
            payment.save()
            
            return Response({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id,
                'order_id': str(order.id)
            }, status=status.HTTP_200_OK)
            
        except stripe.error.StripeError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CheckSessionStatusView(APIView):
    """Check Stripe session payment status"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Check payment session status",
        description="""
        Check the payment status of a Stripe checkout session.
        
        **Returns:**
        - order_id
        - payment status (paid, pending, failed)
        - payment details
        
        Requires authentication.
        """,
        tags=['Payments']
    )
    def get(self, request, session_id):
        try:
            # Retrieve session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            
            # Get payment record
            try:
                payment = Payment.objects.get(
                    stripe_checkout_session_id=session_id,
                    order__user=request.user
                )
            except Payment.DoesNotExist:
                return Response({
                    'error': 'Payment not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Map Stripe payment status to our status
            stripe_status = session.payment_status
            if stripe_status == 'paid':
                payment.status = 'paid'
                payment.stripe_payment_intent_id = session.payment_intent
                payment.transaction_id = session.payment_intent
                payment.payment_date = timezone.now()
                payment.save()
                
                # Update order status
                payment.order.status = 'processing'
                payment.order.save()
                
            elif stripe_status == 'unpaid':
                payment.status = 'pending'
                payment.save()
            
            return Response({
                'order_id': str(payment.order.id),
                'status': payment.status,
                'amount': str(payment.amount),
                'payment_date': payment.payment_date
            }, status=status.HTTP_200_OK)
            
        except stripe.error.StripeError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """Handle Stripe webhooks"""
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Stripe webhook endpoint",
        description="Receives payment events from Stripe. This endpoint is called by Stripe automatically.",
        tags=['Payments']
    )
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return Response({'error': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError:
            return Response({'error': 'Invalid signature'}, status=400)
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            # Get payment
            try:
                payment = Payment.objects.get(
                    stripe_checkout_session_id=session['id']
                )
                
                # Update payment status
                payment.status = 'paid'
                payment.stripe_payment_intent_id = session.get('payment_intent')
                payment.transaction_id = session.get('payment_intent')
                payment.payment_date = timezone.now()
                payment.save()
                
                # Update order status
                payment.order.status = 'processing'
                payment.order.save()
                
            except Payment.DoesNotExist:
                pass
        
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            
            # Update payment to failed
            try:
                payment = Payment.objects.get(
                    stripe_payment_intent_id=payment_intent['id']
                )
                payment.status = 'failed'
                payment.failure_reason = payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')
                payment.save()
            except Payment.DoesNotExist:
                pass
        
        return Response({'status': 'success'}, status=200)


class OrderPaymentDetailView(generics.RetrieveAPIView):
    """Get payment details for an order"""
    
    serializer_class = PaymentDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        order_id = self.kwargs.get('order_id')
        try:
            payment = Payment.objects.get(
                order__id=order_id,
                order__user=self.request.user
            )
            return payment
        except Payment.DoesNotExist:
            from django.http import Http404
            raise Http404("Payment not found for this order")
    
    @extend_schema(
        summary="Get payment details for order",
        description="Retrieve payment information for a specific order. Users can only view their own order payments.",
        tags=['Payments']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)