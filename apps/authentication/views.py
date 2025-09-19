# apps/authentication/views.py

"""
Authentication Views

This module contains all API views for authentication endpoints.
Organized into Authentication and Profile sections.
"""

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from .permissions import IsAdminUser
from drf_spectacular.utils import extend_schema

from .models import User, OTPVerification, LoginAttempt
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    OTPVerificationSerializer,
    ResendOTPSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from apps.common.utils import get_client_ip, get_user_agent, send_email


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

@extend_schema(
    summary="Register new user",
    description="Create user account and send email verification OTP",
    tags=['Authentication']
)
class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user and send OTP for email verification.
    User must verify email before being able to login.
    """
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Handle user registration with OTP generation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user (email_verified=False, can_login=False by default)
        user = serializer.save()
        
        # Create and send OTP for email verification
        otp = OTPVerification.create_otp(user, OTPVerification.EMAIL)
        
        # Send OTP email
        self._send_verification_email(user, otp.otp)
        
        return Response({
            'success': True,
            'message': 'Registration successful. Please check your email for verification code.',
            'data': {
                'user_id': str(user.id),
                'email': user.email,
                'verification_required': True
            }
        }, status=status.HTTP_201_CREATED)
    
    def _send_verification_email(self, user, otp_code):
        """Send verification email with OTP."""
        context = {
            'user_name': user.get_full_name(),
            'otp_code': otp_code,
            'expiry_minutes': getattr(settings, 'OTP_EXPIRY_TIME', 10),
            'site_name': getattr(settings, 'SITE_NAME', 'Our App')
        }
        
        send_email(
            subject=f'Verify your email - {context["site_name"]}',
            template_name='otp_verification',
            context=context,
            recipient_list=[user.email]
        )


class UserLoginView(APIView):
    """
    Authenticate user and return JWT tokens.
    Requires email verification to be completed.
    """

    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="User login",
        description="Authenticate user with email and password (requires email verification)",
        request=UserLoginSerializer,
        tags=['Authentication']
    )
    def post(self, request):
        """Handle user login with verification check."""
        # Add IP and user agent to request data
        data = request.data.copy()
        data['ip_address'] = get_client_ip(request)
        data['user_agent'] = get_user_agent(request)
        
        serializer = UserLoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email_verified': user.email_verified
                },
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh)
                }
            }
        }, status=status.HTTP_200_OK)


class OTPVerificationView(APIView):
    """
    Verify OTP for email verification or password reset.
    Required for users to complete registration process.
    """
    
    permission_classes = [AllowAny]  # Allow unverified users to verify their email
    
    @extend_schema(
        summary="Verify OTP",
        description="Verify OTP code for email verification",
        request=OTPVerificationSerializer,
        tags=['Authentication']
    )
    def post(self, request):
        """Handle OTP verification."""
        # Get user by email from request data
        email = request.data.get('email')
        if not email:
            return Response({
                'success': False,
                'message': 'Email is required for verification'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email.lower().strip())
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OTPVerificationSerializer(
            data=request.data,
            context={'user': user}
        )
        serializer.is_valid(raise_exception=True)
        
        otp_type = serializer.validated_data['otp_type']
        
        # Prepare success message
        if otp_type == OTPVerification.EMAIL:
            message = 'Email verified successfully. You can now login.'
        else:
            message = 'OTP verified successfully'
        
        return Response({
            'success': True,
            'message': message,
            'data': {
                'email_verified': user.email_verified,
                'can_login': user.can_login
            }
        }, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    """
    Resend OTP for email verification.
    Rate limited to prevent abuse.
    """
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Resend OTP",
        description="Resend OTP code for verification (rate limited)",
        request=ResendOTPSerializer,
        tags=['Authentication']
    )
    def post(self, request):
        """Handle OTP resend request."""
        # Get email from request
        email = request.data.get('email')
        if not email:
            return Response({
                'success': False,
                'message': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email.lower().strip())
        except User.DoesNotExist:
            # Don't reveal if email exists
            return Response({
                'success': True,
                'message': 'If the email exists, a new OTP has been sent.'
            }, status=status.HTTP_200_OK)
        
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        otp_type = serializer.validated_data['otp_type']
        
        # Check if already verified
        if otp_type == OTPVerification.EMAIL and user.email_verified:
            return Response({
                'success': False,
                'message': 'Email is already verified'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check rate limiting
        cache_key = f'otp_resend_{user.id}_{otp_type}'
        resend_count = cache.get(cache_key, 0)
        
        if resend_count >= 3:
            return Response({
                'success': False,
                'message': 'Maximum OTP requests exceeded. Please try again in an hour.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Create new OTP
        otp = OTPVerification.create_otp(user, otp_type)
        
        # Send OTP
        if otp_type == OTPVerification.EMAIL:
            context = {
                'user_name': user.get_full_name(),
                'otp_code': otp.otp,
                'expiry_minutes': getattr(settings, 'OTP_EXPIRY_TIME', 10),
                'site_name': getattr(settings, 'SITE_NAME', 'Our App')
            }
            
            send_email(
                subject=f'Verify your email - {context["site_name"]}',
                template_name='otp_verification',
                context=context,
                recipient_list=[user.email]
            )
            
            message = 'OTP sent to your email'
        
        # Update rate limit counter
        cache.set(cache_key, resend_count + 1, 3600)  # Expire in 1 hour
        
        return Response({
            'success': True,
            'message': message,
            'data': {
                'otp_type': otp_type,
                'expires_in': getattr(settings, 'OTP_EXPIRY_TIME', 10) * 60
            }
        }, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """
    Request password reset via email.
    Sends OTP to user's email for password reset.
    """
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Request password reset",
        description="Send OTP to email for password reset",
        request=PasswordResetRequestSerializer,
        tags=['Authentication']
    )
    def post(self, request):
        """Handle password reset request."""
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        # Always return success for security
        response_data = {
            'success': True,
            'message': 'If the email exists, a password reset code has been sent.'
        }
        
        try:
            user = User.objects.get(email=email)
            
            # Check rate limiting
            cache_key = f'password_reset_{email}'
            reset_count = cache.get(cache_key, 0)
            
            if reset_count < 3:  # Max 3 requests per hour
                # Create OTP for password reset
                otp = OTPVerification.create_otp(user, OTPVerification.PASSWORD_RESET)
                
                # Send email
                context = {
                    'user_name': user.get_full_name(),
                    'otp_code': otp.otp,
                    'expiry_minutes': getattr(settings, 'OTP_EXPIRY_TIME', 10),
                    'site_name': getattr(settings, 'SITE_NAME', 'Our App')
                }
                
                send_email(
                    subject=f'Password Reset Request - {context["site_name"]}',
                    template_name='password_reset',
                    context=context,
                    recipient_list=[user.email]
                )
                
                # Update rate limit counter
                cache.set(cache_key, reset_count + 1, 3600)
        
        except User.DoesNotExist:
            pass  # Don't reveal user doesn't exist
        
        return Response(response_data, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with OTP.
    Verifies OTP and sets new password.
    """
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Confirm password reset",
        description="Verify OTP and set new password",
        request=PasswordResetConfirmSerializer,
        tags=['Authentication']
    )
    def post(self, request):
        """Handle password reset confirmation."""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        otp_code = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']
        
        # Find valid OTP
        otp_instance = OTPVerification.objects.filter(
            otp=otp_code,
            otp_type=OTPVerification.PASSWORD_RESET,
            is_used=False
        ).first()
        
        if not otp_instance or otp_instance.is_expired:
            return Response({
                'success': False,
                'message': 'Invalid or expired OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP and reset password
        if otp_instance.verify(otp_code):
            user = otp_instance.user
            user.set_password(new_password)
            user.save()
            
            # Send confirmation email
            context = {
                'user_name': user.get_full_name(),
                'site_name': getattr(settings, 'SITE_NAME', 'Our App')
            }
            
            send_email(
                subject=f'Password Reset Successful - {context["site_name"]}',
                template_name='password_reset_success',
                context=context,
                recipient_list=[user.email]
            )
            
            return Response({
                'success': True,
                'message': 'Password reset successful. You can now login with your new password.'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Invalid OTP'
        }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Logout user and blacklist refresh token.
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="User logout",
        description="Logout user and blacklist refresh token",
        tags=['Authentication']
    )
    def post(self, request):
        """Handle user logout."""
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'success': True,
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        
        except Exception:
            return Response({
                'success': False,
                'message': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with email verification check.
    """
    
    serializer_class = CustomTokenObtainPairSerializer
    
    @extend_schema(
        summary="Obtain JWT token pair",
        description="Get access and refresh tokens (requires email verification)",
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        """Handle token obtain request."""
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT token refresh view.
    """
    
    @extend_schema(
        summary="Refresh JWT token",
        description="Get new access token using refresh token",
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        """Handle token refresh request."""
        return super().post(request, *args, **kwargs)


# ============================================================================
# PROFILE VIEWS
# ============================================================================

# class UserProfileView(generics.RetrieveUpdateAPIView):
#     """
#     Get and update current user's profile information.
#     Requires authentication.
#     """
    
#     serializer_class = UserProfileSerializer
#     permission_classes = [IsAuthenticated]
    
#     def get_object(self):
#         """Return the current authenticated user."""
#         return self.request.user
    
#     @extend_schema(
#         summary="Get user profile",
#         description="Retrieve current user's profile information",
#         responses={200: UserProfileSerializer},
#         tags=['User Profile']
#     )
#     def get(self, request, *args, **kwargs):
#         """Handle profile retrieval."""
#         return super().get(request, *args, **kwargs)
    
#     @extend_schema(
#         summary="Update user profile",
#         description="Update current user's profile information",
#         request=UserProfileSerializer,
#         responses={200: UserProfileSerializer},
#         tags=['User Profile']
#     )
#     def update(self, request, *args, **kwargs):
#         """Handle profile update."""
#         partial = kwargs.pop('partial', True)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
        
#         return Response({
#             'success': True,
#             'message': 'Profile updated successfully',
#             'data': serializer.data
#         }, status=status.HTTP_200_OK)



class UserProfileView(APIView):
    """
    Get and update current user's profile information.
    Requires authentication.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Return the current authenticated user."""
        return self.request.user
    
    @extend_schema(
        summary="Get user profile",
        description="Retrieve current user's profile information",
        responses={200: UserProfileSerializer},
        tags=['User Profile']
    )
    def get(self, request):
        """Handle profile retrieval."""
        user = self.get_object()
        serializer = UserProfileSerializer(user)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Update user profile",
        description="Update current user's profile information",
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer},
        tags=['User Profile']
    )
    def patch(self, request):
      """Handle profile update."""
      user = self.get_object()
      serializer = UserProfileSerializer(
        user, 
        data=request.data, 
        partial=True,
        context={'request': request}  # Add this line
    )
      serializer.is_valid(raise_exception=True)
      serializer.save()
    
      return Response({
        'success': True,
        'message': 'Profile updated successfully',
        'data': serializer.data
    }, status=status.HTTP_200_OK)

class PasswordChangeView(APIView):
    """
    Change password for authenticated user.
    Requires current password verification.
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Change password",
        description="Change current user's password",
        request=PasswordChangeSerializer,
        tags=['User Profile']
    )
    def post(self, request):
        """Handle password change."""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Change password
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Send confirmation email
        context = {
            'user_name': user.get_full_name(),
            'site_name': getattr(settings, 'SITE_NAME', 'Our App')
        }
        
        send_email(
            subject=f'Password Changed - {context["site_name"]}',
            template_name='password_changed',
            context=context,
            recipient_list=[user.email]
        )
        
        return Response({
            'success': True,
            'message': 'Password changed successfully. Please login with your new password.'
        }, status=status.HTTP_200_OK)
 
class PromoteUserView(APIView):
    """
    Promote a customer to admin role.
    Only accessible by existing admin users.
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Promote user to admin",
        description="Promote a customer user to admin role (admin only)",
        tags=['Authentication']
    )
    def patch(self, request, user_id):
        """Handle user role promotion."""
        # Check if current user is admin
        if getattr(request.user, 'role', None) != 'admin':
            return Response({
                'success': False,
                'message': 'Only admin users can promote others'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id)
            user.role = 'admin'
            user.save(update_fields=['role'])
            
            return Response({
                'success': True,
                'message': f'User {user.email} promoted to admin successfully'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
from rest_framework_simplejwt.views import TokenVerifyView

class CustomTokenVerifyView(TokenVerifyView):
    """
    Custom JWT token verify view with proper tagging.
    """
    
    @extend_schema(
        summary="Verify JWT token",
        description="Verify if a JWT token is valid",
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        """Handle token verification request."""
        return super().post(request, *args, **kwargs)       
        