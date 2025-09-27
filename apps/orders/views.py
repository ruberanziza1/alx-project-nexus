# # apps/orders/views.py

# """
# Order Views

# Views for order management.
# """

# from rest_framework import generics, status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from django.shortcuts import get_object_or_404
# from drf_spectacular.utils import extend_schema

# from .models import Order
# from .serializers import (
#     OrderListSerializer,
#     OrderDetailSerializer,
#     CreateOrderSerializer,
#     UpdateOrderStatusSerializer
# )
# from .permissions import IsOrderOwner, IsAdminUser


# class OrderListCreateView(generics.ListCreateAPIView):
#     """
#     List user's orders OR Create new order from cart
#     """
    
#     permission_classes = [IsAuthenticated]
    
#     def get_serializer_class(self):
#         if self.request.method == 'POST':
#             return CreateOrderSerializer
#         return OrderListSerializer
    
#     def get_queryset(self):
#         """Return only current user's orders"""
#         return Order.objects.filter(user=self.request.user).prefetch_related('items')
    
#     @extend_schema(
#         summary="List user's orders",
#         description="Get list of all orders for the authenticated user, sorted by most recent first.",
#         tags=['Orders']
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
    
#     @extend_schema(
#         summary="Create order from cart",
#         description="""
#         Create a new order from current cart items.
        
#         **Process:**
#         1. Validates cart has items
#         2. Checks stock availability
#         3. Creates order with items
#         4. Reduces product stock
#         5. Clears cart
        
#         **Optional shipping information can be provided.**
        
#         Requires authentication.
#         """,
#         tags=['Orders']
#     )
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         order = serializer.save()
        
#         # Return order details
#         order_serializer = OrderDetailSerializer(order, context={'request': request})
#         return Response(
#             {
#                 'message': 'Order placed successfully',
#                 'order': order_serializer.data
#             },
#             status=status.HTTP_201_CREATED
#         )


# class OrderDetailView(generics.RetrieveAPIView):
#     """
#     Get order details
#     """
    
#     serializer_class = OrderDetailSerializer
#     permission_classes = [IsAuthenticated, IsOrderOwner]
#     lookup_field = 'pk'
    
#     def get_queryset(self):
#         """Return only current user's orders"""
#         return Order.objects.filter(user=self.request.user).prefetch_related('items', 'items__product')
    
#     @extend_schema(
#         summary="Get order details",
#         description="Retrieve complete order information including items, status, and shipping details. Users can only view their own orders.",
#         tags=['Orders']
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)


# class OrderUpdateStatusView(generics.UpdateAPIView):
#     """
#     Update order status (Admin only)
#     """
    
#     serializer_class = UpdateOrderStatusSerializer
#     permission_classes = [IsAuthenticated, IsAdminUser]
#     lookup_field = 'pk'
#     queryset = Order.objects.all()
    
#     @extend_schema(
#         summary="Update order status",
#         description="""
#         Update order status (Admin only).
        
#         **Valid status transitions:**
#         - pending → processing, cancelled
#         - processing → shipped, cancelled
#         - shipped → delivered, cancelled
#         - delivered → (final state, no changes)
#         - cancelled → (final state, no changes)
        
#         Requires admin authentication.
#         """,
#         tags=['Orders']
#     )
#     def patch(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
        
#         return Response({
#             'message': f'Order status updated to {instance.get_status_display()}',
#             'status': instance.status
#         })


# class OrderCancelView(generics.UpdateAPIView):
#     """
#     Cancel order (User can cancel own pending/processing orders)
#     """
    
#     permission_classes = [IsAuthenticated, IsOrderOwner]
#     lookup_field = 'pk'
    
#     def get_queryset(self):
#         """Return only current user's orders"""
#         return Order.objects.filter(user=self.request.user)
    
#     @extend_schema(
#         summary="Cancel order",
#         description="""
#         Cancel an order (only pending or processing orders can be cancelled by users).
        
#         **Stock will be restored** for cancelled orders.
        
#         Requires authentication.
#         """,
#         tags=['Orders']
#     )
#     def patch(self, request, *args, **kwargs):
#         order = self.get_object()
        
#         # Check if order can be cancelled
#         if order.status not in ['pending', 'processing']:
#             return Response(
#                 {'error': f'Cannot cancel order with status: {order.get_status_display()}'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         # Restore stock for all items
#         for item in order.items.all():
#             item.product.stock_quantity += item.quantity
#             item.product.save()
        
#         # Update order status
#         order.status = 'cancelled'
#         order.save()
        
#         return Response({
#             'message': 'Order cancelled successfully',
#             'order_id': str(order.id),
#             'status': order.status
#         })




# apps/orders/views.py

"""
Order Views

Views for order management.
"""

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from .models import Order
from .serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    CreateOrderSerializer,
    UpdateOrderStatusSerializer
)
from .permissions import IsOrderOwner, IsAdminUser


class OrderListCreateView(generics.ListCreateAPIView):
    """
    List user's orders OR Create new order from cart
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderListSerializer
    
    def get_queryset(self):
        """Return only current user's orders"""
        return Order.objects.filter(user=self.request.user).prefetch_related('items')
    
    @extend_schema(
        summary="List user's orders",
        description="Get list of all orders for the authenticated user, sorted by most recent first.",
        tags=['Orders']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create order from cart",
        description="""
        Create a new order from current cart items.
        
        **Process:**
        1. Validates cart has items
        2. Checks stock availability
        3. Creates order with items
        4. Reduces product stock
        5. Clears cart
        
        **Optional shipping information can be provided.**
        
        Requires authentication.
        """,
        tags=['Orders']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        # Return order details
        order_serializer = OrderDetailSerializer(order, context={'request': request})
        return Response(
            {
                'message': 'Order placed successfully',
                'order': order_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class OrderDetailView(generics.RetrieveAPIView):
    """
    Get order details
    """
    
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated, IsOrderOwner]
    lookup_field = 'pk'
    
    def get_queryset(self):
        """Return only current user's orders"""
        return Order.objects.filter(user=self.request.user).prefetch_related('items', 'items__product')
    
    @extend_schema(
        summary="Get order details",
        description="Retrieve complete order information including items, status, and shipping details. Users can only view their own orders.",
        tags=['Orders']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class OrderUpdateStatusView(generics.UpdateAPIView):
    """
    Update order status (Admin only)
    """
    
    serializer_class = UpdateOrderStatusSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_field = 'pk'
    queryset = Order.objects.all()
    http_method_names = ['patch']  # Only allow PATCH, no PUT
    
    @extend_schema(
        summary="Update order status",
        description="""
        Update order status (Admin only).
        
        **Valid status transitions:**
        - pending → processing, cancelled
        - processing → shipped, cancelled
        - shipped → delivered, cancelled
        - delivered → (final state, no changes)
        - cancelled → (final state, no changes)
        
        Requires admin authentication.
        """,
        tags=['Orders']
    )
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': f'Order status updated to {instance.get_status_display()}',
            'status': instance.status
        })


class OrderCancelView(generics.UpdateAPIView):
    """
    Cancel order (User can cancel own pending/processing orders)
    """
    
    permission_classes = [IsAuthenticated, IsOrderOwner]
    lookup_field = 'pk'
    http_method_names = ['patch']  # Only allow PATCH, no PUT
    
    def get_queryset(self):
        """Return only current user's orders"""
        return Order.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="Cancel order",
        description="""
        Cancel an order (only pending or processing orders can be cancelled by users).
        
        **Stock will be restored** for cancelled orders.
        
        Requires authentication.
        """,
        tags=['Orders']
    )
    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        
        # Check if order can be cancelled
        if order.status not in ['pending', 'processing']:
            return Response(
                {'error': f'Cannot cancel order with status: {order.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Restore stock for all items
        for item in order.items.all():
            item.product.stock_quantity += item.quantity
            item.product.save()
        
        # Update order status
        order.status = 'cancelled'
        order.save()
        
        return Response({
            'message': 'Order cancelled successfully',
            'order_id': str(order.id),
            'status': order.status
        })