# Complete API Testing Guide - Authentication System
# Base URL
BASE_URL="http://localhost:8000/api/v1/auth"

# ============================================================================
# 1. USER REGISTRATION
# ============================================================================

# Test: Register new user
curl -X POST $BASE_URL/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe"
  }'

# Expected Response (201 Created):
{
  "success": true,
  "message": "Registration successful. Please check your email for verification code.",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    "verification_required": true
  }
}

# Error Case - Duplicate email (400 Bad Request):
{
  "email": ["An account with this email already exists."]
}

# Error Case - Password mismatch (400 Bad Request):
{
  "password_confirm": ["Passwords do not match."]
}

# ============================================================================
# 2. OTP VERIFICATION (Required before login)
# ============================================================================

# Test: Verify OTP (check console logs for OTP code)
curl -X POST $BASE_URL/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "otp": "123456",
    "otp_type": "email"
  }'

# Expected Response (200 OK):
{
  "success": true,
  "message": "Email verified successfully. You can now login.",
  "data": {
    "email_verified": true,
    "can_login": true
  }
}

# Error Case - Invalid OTP (400 Bad Request):
{
  "otp": ["Invalid OTP. 2 attempts remaining."]
}

# Error Case - Expired OTP (400 Bad Request):
{
  "otp": ["OTP has expired. Please request a new one."]
}

# ============================================================================
# 3. RESEND OTP
# ============================================================================

# Test: Resend OTP
curl -X POST $BASE_URL/resend-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "otp_type": "email"
  }'

# Expected Response (200 OK):
{
  "success": true,
  "message": "OTP sent to your email",
  "data": {
    "otp_type": "email",
    "expires_in": 600
  }
}

# Error Case - Already verified (400 Bad Request):
{
  "success": false,
  "message": "Email is already verified"
}

# ============================================================================
# 4. USER LOGIN (Only after email verification)
# ============================================================================

# Test: Login with verified user
curl -X POST $BASE_URL/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'

# Expected Response (200 OK):
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "email_verified": true
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  }
}

# Error Case - Email not verified (400 Bad Request):
{
  "non_field_errors": ["Please verify your email before logging in."]
}

# Error Case - Invalid credentials (400 Bad Request):
{
  "non_field_errors": ["Invalid email or password."]
}

# Save tokens for next requests
ACCESS_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
REFRESH_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# ============================================================================
# 5. JWT TOKEN OPERATIONS
# ============================================================================

# Test: Obtain JWT token pair (alternative to login)
curl -X POST $BASE_URL/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'

# Expected Response (200 OK):
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "email_verified": true,
    "is_complete_profile": false
  }
}

# Test: Refresh access token
curl -X POST $BASE_URL/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "'$REFRESH_TOKEN'"
  }'

# Expected Response (200 OK):
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

# Test: Verify token validity
curl -X POST $BASE_URL/token/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "'$ACCESS_TOKEN'"
  }'

# Expected Response - Valid token (200 OK):
{}

# Error Case - Invalid token (401 Unauthorized):
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}

# ============================================================================
# 6. PASSWORD RESET FLOW
# ============================================================================

# Test: Request password reset
curl -X POST $BASE_URL/password-reset/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com"
  }'

# Expected Response (200 OK):
{
  "success": true,
  "message": "If the email exists, a password reset code has been sent."
}

# Test: Confirm password reset (use OTP from email/logs)
curl -X POST $BASE_URL/password-reset/confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "otp": "123456",
    "new_password": "NewSecurePass456",
    "new_password_confirm": "NewSecurePass456"
  }'

# Expected Response (200 OK):
{
  "success": true,
  "message": "Password reset successful. You can now login with your new password."
}

# Error Case - Invalid OTP (400 Bad Request):
{
  "success": false,
  "message": "Invalid or expired OTP"
}

# ============================================================================
# 7. USER PROFILE OPERATIONS (Requires Authentication)
# ============================================================================

# Test: Get user profile
curl -X GET $BASE_URL/profile/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json"

# Expected Response (200 OK):
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone_number": null,
    "email_verified": true,
    "avatar": null,
    "bio": "",
    "date_joined": "2025-09-17T20:30:45.123456Z",
    "last_login": "2025-09-17T20:45:12.789012Z"
  }
}

# Test: Update user profile
curl -X PATCH $BASE_URL/profile/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jonathan",
    "last_name": "Smith",
    "bio": "Software Engineer",
    "phone_number": "+1234567890"
  }'

# Expected Response (200 OK):
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    "first_name": "Jonathan",
    "last_name": "Smith",
    "full_name": "Jonathan Smith",
    "phone_number": "+1234567890",
    "email_verified": true,
    "avatar": null,
    "bio": "Software Engineer",
    "date_joined": "2025-09-17T20:30:45.123456Z",
    "last_login": "2025-09-17T20:45:12.789012Z"
  }
}

# Error Case - No auth token (401 Unauthorized):
{
  "detail": "Authentication credentials were not provided."
}

# ============================================================================
# 8. CHANGE PASSWORD (Authenticated users)
# ============================================================================

# Test: Change password
curl -X POST $BASE_URL/profile/change-password/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "SecurePass123",
    "new_password": "NewPassword789",
    "new_password_confirm": "NewPassword789"
  }'

# Expected Response (200 OK):
{
  "success": true,
  "message": "Password changed successfully. Please login with your new password."
}

# Error Case - Wrong old password (400 Bad Request):
{
  "old_password": ["Your old password is incorrect."]
}

# Error Case - Password mismatch (400 Bad Request):
{
  "new_password_confirm": ["New passwords do not match."]
}

# ============================================================================
# 9. LOGOUT
# ============================================================================

# Test: Logout (blacklist refresh token)
curl -X POST $BASE_URL/logout/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "'$REFRESH_TOKEN'"
  }'

# Expected Response (200 OK):
{
  "success": true,
  "message": "Logout successful"
}

# Error Case - Invalid token (400 Bad Request):
{
  "success": false,
  "message": "Invalid token"
}

# ============================================================================
# ERROR TESTING SCENARIOS
# ============================================================================

# Test: Login without email verification (should fail)
curl -X POST $BASE_URL/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "unverified@example.com",
    "password": "password123"
  }'

# Expected Response (400 Bad Request):
{
  "non_field_errors": ["Please verify your email before logging in."]
}

# Test: Access protected endpoint without token (should fail)
curl -X GET $BASE_URL/profile/ \
  -H "Content-Type: application/json"

# Expected Response (401 Unauthorized):
{
  "detail": "Authentication credentials were not provided."
}

# Test: Use expired/invalid access token
curl -X GET $BASE_URL/profile/ \
  -H "Authorization: Bearer invalid_token" \
  -H "Content-Type: application/json"

# Expected Response (401 Unauthorized):
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}

# ============================================================================
# TESTING SUMMARY
# ============================================================================

# Authentication Flow:
# 1. Register ✅ → 2. Verify OTP ✅ → 3. Login ✅ → 4. Use Protected APIs ✅

# Error Handling:
# - Invalid credentials ❌
# - Missing authentication ❌  
# - Expired tokens ❌
# - Invalid data formats ❌

# Success Indicators:
# - 200/201 status codes with success: true
# - Proper JWT tokens returned
# - Protected endpoints accessible with valid tokens
# - Email verification enforced before login