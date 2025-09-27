from django.urls import path
# Remove this import:
# from rest_framework_simplejwt.views import TokenVerifyView

from .views import (
    # Authentication Views
    UserRegistrationView,
    UserLoginView,
    OTPVerificationView,
    ResendOTPView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    LogoutView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,  # Add this custom view
    
    # Profile Views
    UserProfileView,
    PasswordChangeView,
    PromoteUserView,
)

app_name = 'authentication'

urlpatterns = [
    # Step 1: Registration
    path('register/', UserRegistrationView.as_view(), name='register'),
    
    # Step 2: Email Verification  
    path('verify-otp/', OTPVerificationView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    
    # Step 3: Login & Logout
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # JWT Token Management
    path('token/', CustomTokenObtainPairView.as_view(), name='token-obtain'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', CustomTokenVerifyView.as_view(), name='token-verify'),  # Use custom view
    
    # Password Reset Flow
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Profile Management
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/change-password/', PasswordChangeView.as_view(), name='change-password'),
    path('promote/<uuid:user_id>/', PromoteUserView.as_view(), name='promote-user'),
]