# # apps/carts/views.py

# """
# Cart Views

# Complete cart management API views.
# All cart operations require user authentication.
# """

# from rest_framework import generics, status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from django.shortcuts import get_object_or_404
# from drf_spectacular.utils import extend_schema
# from django.db import transaction

# from .models import Cart, CartItem
# from .serializers import (
#     CartSerializer,
#     AddToCartSerializer,
#     UpdateCartItemSerializer,
#     CartItemSerializer
# )
# from apps.products.models import Product


# class CartView(generics.RetrieveAPIView):
#     """
#     GET /cart/ - View current user's cart
    
#     Returns the user's cart with all items, totals, and calculations.
#     Creates an empty cart if user doesn't have one.
#     """
    
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated]
    
#     def get_object(self):
#         """Get or create user's cart"""
#         cart, created = Cart.objects.get_or_create(user=self.request.user)
#         return cart
    
#     @extend_schema(
#         summary="Get user's cart",
#         description="Retrieve the current user's shopping cart with all items and totals",
#         tags=['Cart']
#     )
#     def get(self, request, *args, **kwargs):
#         """Handle cart retrieval request"""
#         try:
#             cart = self.get_object()
#             serializer = self.get_serializer(cart)
            
#             return Response({
#                 'success': True,
#                 'message': 'Cart retrieved successfully',
#                 'data': serializer.data
#             })
            
#         except Exception as e:
#             return Response({
#                 'success': False,
#                 'message': 'Failed to retrieve cart',
#                 'error': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class AddToCartView(generics.CreateAPIView):
#     """
#     POST /cart/add/ - Add a product to the cart
    
#     Adds a product to the user's cart or updates quantity if already exists.
#     """
    
#     serializer_class = AddToCartSerializer
#     permission_classes = [IsAuthenticated]
    
#     @extend_schema(
#         summary="Add product to cart",
#         description="Add a product to the current user's cart or update quantity if it already exists",
#         request=AddToCartSerializer,
#         responses={201: CartItemSerializer},
#         tags=['Cart']
#     )
#     def post(self, request, *args, **kwargs):
#         """Handle add to cart request"""
#         try:
#             serializer = self.get_serializer(data=request.data)
            
#             if not serializer.is_valid():
#                 return Response({
#                     'success': False,
#                     'message': 'Validation failed',
#                     'errors': serializer.errors
#                 }, status=status.HTTP_400_BAD_REQUEST)
            
#             validated_data = serializer.validated_data
#             product = validated_data['product']
#             quantity = validated_data['quantity']
            
#             # Get or create user's cart
#             cart, created = Cart.objects.get_or_create(user=request.user)
            
#             # Check if item already exists in cart
#             cart_item, item_created = CartItem.objects.get_or_create(
#                 cart=cart,
#                 product=product,
#                 defaults={'quantity': quantity}
#             )
            
#             if not item_created:
#                 # Item exists, update quantity
#                 new_quantity = cart_item.quantity + quantity
                
#                 # Check stock availability for new quantity
#                 if new_quantity > product.stock_quantity:
#                     return Response({
#                         'success': False,
#                         'message': 'Insufficient stock',
#                         'error': f'Only {product.stock_quantity} items available. You have {cart_item.quantity} in cart.'
#                     }, status=status.HTTP_400_BAD_REQUEST)
                
#                 cart_item.quantity = new_quantity
#                 cart_item.save()
#                 message = f'Updated quantity to {new_quantity}'
#             else:
#                 message = f'Added {quantity} item(s) to cart'
            
#             # Return cart item data
#             response_serializer = CartItemSerializer(cart_item, context={'request': request})
            
#             return Response({
#                 'success': True,
#                 'message': message,
#                 'data': response_serializer.data
#             }, status=status.HTTP_201_CREATED if item_created else status.HTTP_200_OK)
            
#         except Exception as e:
#             return Response({
#                 'success': False,
#                 'message': 'Failed to add item to cart',
#                 'error': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class UpdateCartItemView(generics.UpdateAPIView):
#     """
#     PUT /cart/update/{item_id}/ - Update cart item quantity
    
#     Updates the quantity of a specific item in the user's cart.
#     """
    
#     serializer_class = UpdateCartItemSerializer
#     permission_classes = [IsAuthenticated]
#     lookup_field = 'pk'
    
#     def get_queryset(self):
#         """Get cart items for current user only"""
#         return CartItem.objects.filter(cart__user=self.request.user).select_related('product', 'cart')
    
#     @extend_schema(
#         summary="Update cart item quantity",
#         description="Update the quantity of a specific item in the user's cart",
#         request=UpdateCartItemSerializer,
#         responses={200: CartItemSerializer},
#         tags=['Cart']
#     )
#     def put(self, request, *args, **kwargs):
#         """Handle cart item update request"""
#         try:
#             cart_item = self.get_object()
            
#             serializer = self.get_serializer(
#                 data=request.data,
#                 context={'cart_item': cart_item}
#             )
            
#             if not serializer.is_valid():
#                 return Response({
#                     'success': False,
#                     'message': 'Validation failed',
#                     'errors': serializer.errors
#                 }, status=status.HTTP_400_BAD_REQUEST)
            
#             new_quantity = serializer.validated_data['quantity']
            
#             # Update quantity
#             cart_item.quantity = new_quantity
#             cart_item.save()
            
#             # Return updated cart item data
#             response_serializer = CartItemSerializer(cart_item, context={'request': request})
            
#             return Response({
#                 'success': True,
#                 'message': f'Updated quantity to {new_quantity}',
#                 'data': response_serializer.data
#             })
            
#         except CartItem.DoesNotExist:
#             return Response({
#                 'success': False,
#                 'message': 'Cart item not found',
#                 'error': 'Item not found in your cart'
#             }, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({
#                 'success': False,
#                 'message': 'Failed to update cart item',
#                 'error': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class RemoveFromCartView(generics.DestroyAPIView):
#     """
#     DELETE /cart/remove/{item_id}/ - Remove product from cart
    
#     Removes a specific item from the user's cart completely.
#     """
    
#     permission_classes = [IsAuthenticated]
#     lookup_field = 'pk'
    
#     def get_queryset(self):
#         """Get cart items for current user only"""
#         return CartItem.objects.filter(cart__user=self.request.user).select_related('product', 'cart')
    
#     @extend_schema(
#         summary="Remove item from cart",
#         description="Remove a specific item from the user's cart completely",
#         tags=['Cart']
#     )
#     def delete(self, request, *args, **kwargs):
#         """Handle remove from cart request"""
#         try:
#             cart_item = self.get_object()
#             product_name = cart_item.product.name
#             quantity = cart_item.quantity
            
#             # Remove the item
#             cart_item.delete()
            
#             return Response({
#                 'success': True,
#                 'message': f'Removed {quantity}x {product_name} from cart',
#                 'data': {
#                     'removed_item': {
#                         'product_name': product_name,
#                         'quantity': quantity
#                     }
#                 }
#             })
            
#         except CartItem.DoesNotExist:
#             return Response({
#                 'success': False,
#                 'message': 'Cart item not found',
#                 'error': 'Item not found in your cart'
#             }, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({
#                 'success': False,
#                 'message': 'Failed to remove item from cart',
#                 'error': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ClearCartView(generics.GenericAPIView):
#     """
#     DELETE /cart/clear/ - Clear entire cart
    
#     Removes all items from the user's cart.
#     """
    
#     permission_classes = [IsAuthenticated]
    
#     @extend_schema(
#         summary="Clear entire cart",
#         description="Remove all items from the user's cart",
#         tags=['Cart']
#     )
#     def delete(self, request, *args, **kwargs):
#         """Handle clear cart request"""
#         try:
#             # Get user's cart
#             try:
#                 cart = Cart.objects.get(user=request.user)
#                 items_count = cart.total_items
                
#                 # Clear all items
#                 cart.clear()
                
#                 return Response({
#                     'success': True,
#                     'message': f'Removed {items_count} items from cart',
#                     'data': {
#                         'cleared_items': items_count
#                     }
#                 })
                
#             except Cart.DoesNotExist:
#                 return Response({
#                     'success': True,
#                     'message': 'Cart is already empty',
#                     'data': {
#                         'cleared_items': 0
#                     }
#                 })
            
#         except Exception as e:
#             return Response({
#                 'success': False,
#                 'message': 'Failed to clear cart',
#                 'error': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# apps/carts/views.py

"""
Cart Views - Consolidated

Consolidated cart management API views.
All cart operations require user authentication.
"""

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from django.db import transaction

from .models import Cart, CartItem
from .serializers import (
    CartSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
    CartItemSerializer
)
from apps.products.models import Product


class CartView(APIView):
    """
    GET /carts/ - View current user's cart
    POST /carts/add/ - Add product to cart
    DELETE /carts/clear/ - Clear entire cart
    
    Consolidated cart operations endpoint.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_user_cart(self):
        """Get or create user's cart"""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    @extend_schema(
        summary="Get user's cart",
        description="Retrieve the current user's shopping cart with all items and totals",
        responses={200: CartSerializer},
        tags=['Cart']
    )
    def get(self, request):
        """Handle cart retrieval request"""
        try:
            cart = self.get_user_cart()
            serializer = CartSerializer(cart, context={'request': request})
            
            return Response({
                'success': True,
                'message': 'Cart retrieved successfully',
                'data': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to retrieve cart',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Add product to cart",
        description="Add a product to the current user's cart or update quantity if it already exists",
        request=AddToCartSerializer,
        responses={201: CartItemSerializer},
        tags=['Cart']
    )
    def post(self, request):
        """Handle add to cart request"""
        try:
            serializer = AddToCartSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            product = validated_data['product']
            quantity = validated_data['quantity']
            
            # Get or create user's cart
            cart = self.get_user_cart()
            
            # Check if item already exists in cart
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not item_created:
                # Item exists, update quantity
                new_quantity = cart_item.quantity + quantity
                
                # Check stock availability for new quantity
                if new_quantity > product.stock_quantity:
                    return Response({
                        'success': False,
                        'message': 'Insufficient stock',
                        'error': f'Only {product.stock_quantity} items available. You have {cart_item.quantity} in cart.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                cart_item.quantity = new_quantity
                cart_item.save()
                message = f'Updated quantity to {new_quantity}'
                status_code = status.HTTP_200_OK
            else:
                message = f'Added {quantity} item(s) to cart'
                status_code = status.HTTP_201_CREATED
            
            # Return cart item data
            response_serializer = CartItemSerializer(cart_item, context={'request': request})
            
            return Response({
                'success': True,
                'message': message,
                'data': response_serializer.data
            }, status=status_code)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to add item to cart',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Clear entire cart",
        description="Remove all items from the user's cart",
        tags=['Cart']
    )
    def delete(self, request):
        """Handle clear cart request"""
        try:
            # Get user's cart
            try:
                cart = Cart.objects.get(user=request.user)
                items_count = cart.total_items
                
                # Clear all items
                cart.clear()
                
                return Response({
                    'success': True,
                    'message': f'Removed {items_count} items from cart',
                    'data': {
                        'cleared_items': items_count
                    }
                })
                
            except Cart.DoesNotExist:
                return Response({
                    'success': True,
                    'message': 'Cart is already empty',
                    'data': {
                        'cleared_items': 0
                    }
                })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to clear cart',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CartItemView(APIView):
    """
    PUT /carts/update/{item_id}/ - Update cart item quantity
    DELETE /carts/remove/{item_id}/ - Remove item from cart
    
    Consolidated cart item operations.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_cart_item(self, item_id):
        """Get cart item for current user"""
        return get_object_or_404(
            CartItem.objects.select_related('product', 'cart'),
            id=item_id,
            cart__user=self.request.user
        )
    
    @extend_schema(
        summary="Update cart item quantity",
        description="Update the quantity of a specific item in the user's cart",
        request=UpdateCartItemSerializer,
        responses={200: CartItemSerializer},
        tags=['Cart']
    )
    def put(self, request, item_id):
        """Handle cart item update request"""
        try:
            cart_item = self.get_cart_item(item_id)
            
            serializer = UpdateCartItemSerializer(
                data=request.data,
                context={'cart_item': cart_item}
            )
            
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            new_quantity = serializer.validated_data['quantity']
            
            # Update quantity
            cart_item.quantity = new_quantity
            cart_item.save()
            
            # Return updated cart item data
            response_serializer = CartItemSerializer(cart_item, context={'request': request})
            
            return Response({
                'success': True,
                'message': f'Updated quantity to {new_quantity}',
                'data': response_serializer.data
            })
            
        except CartItem.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Cart item not found',
                'error': 'Item not found in your cart'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to update cart item',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Partial update cart item",
        description="Partially update cart item quantity",
        request=UpdateCartItemSerializer,
        responses={200: CartItemSerializer},
        tags=['Cart']
    )
    def patch(self, request, item_id):
        """Handle partial cart item update (same as PUT for quantity)"""
        return self.put(request, item_id)
    
    @extend_schema(
        summary="Remove item from cart",
        description="Remove a specific item from the user's cart completely",
        tags=['Cart']
    )
    def delete(self, request, item_id):
        """Handle remove from cart request"""
        try:
            cart_item = self.get_cart_item(item_id)
            product_name = cart_item.product.name
            quantity = cart_item.quantity
            
            # Remove the item
            cart_item.delete()
            
            return Response({
                'success': True,
                'message': f'Removed {quantity}x {product_name} from cart',
                'data': {
                    'removed_item': {
                        'product_name': product_name,
                        'quantity': quantity
                    }
                }
            })
            
        except CartItem.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Cart item not found',
                'error': 'Item not found in your cart'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to remove item from cart',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)