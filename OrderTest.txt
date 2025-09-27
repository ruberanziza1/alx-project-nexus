# Complete Order API Testing Guide

## Prerequisites

1. **Server running:** `python manage.py runserver`
2. **Authentication token ready** (from login API)
3. **Swagger UI:** `http://localhost:8000/api/schema/swagger-ui/`

---

## Testing Flow (Step by Step)

### STEP 1: Setup - Create Products

First, ensure you have products in your database.

```json
POST /api/v1/products/

{
  "name": "Laptop",
  "description": "Gaming laptop",
  "price": 1200.00,
  "category": "Electronics",
  "stock_quantity": 10
}
```

Copy the product `id` from response.

---

### STEP 2: Add Items to Cart

Add products to your cart before creating an order.

**Request:**
```json
POST /api/v1/carts/

{
  "product_id": "your-product-uuid-here",
  "quantity": 2
}
```

**Expected Response:**
```json
{
  "message": "Product added to cart successfully",
  "cart": {
    "id": "cart-uuid",
    "items": [
      {
        "product_name": "Laptop",
        "quantity": 2,
        "unit_price": "1200.00",
        "subtotal": "2400.00"
      }
    ],
    "total_items": 2,
    "total_price": "2400.00"
  }
}
```

**Add more items if needed:**
```json
POST /api/v1/carts/

{
  "product_id": "another-product-uuid",
  "quantity": 1
}
```

---

### STEP 3: View Your Cart

Check your cart before placing order.

```
GET /api/v1/carts/
```

**Expected Response:**
```json
{
  "id": "cart-uuid",
  "items": [
    {
      "product_name": "Laptop",
      "quantity": 2,
      "subtotal": "2400.00"
    }
  ],
  "total_items": 2,
  "total_price": "2400.00"
}
```

---

### STEP 4: Create Order from Cart

**Important:** Your cart must have items before creating an order.

**Request:**
```json
POST /api/v1/orders/

{
  "shipping_address": "123 Main Street",
  "shipping_city": "Kigali",
  "shipping_country": "Rwanda",
  "shipping_postal_code": "00100",
  "order_notes": "Please deliver after 5pm"
}
```

**Note:** All fields are optional. You can even send empty body `{}`

**Expected Response:**
```json
{
  "message": "Order placed successfully",
  "order": {
    "id": "order-uuid-here",
    "user_email": "user@example.com",
    "status": "pending",
    "status_display": "Pending",
    "subtotal": "2400.00",
    "total_amount": "2400.00",
    "total_items": 2,
    "shipping_address": "123 Main Street",
    "shipping_city": "Kigali",
    "items": [
      {
        "id": "item-uuid",
        "product_name": "Laptop",
        "quantity": 2,
        "unit_price": "1200.00",
        "subtotal": "2400.00"
      }
    ],
    "created_at": "2025-09-25T14:30:00Z"
  }
}
```

**What happens after order creation:**
- Cart is cleared automatically
- Product stock is reduced
- Order status is set to "pending"

**Copy the order `id` for next tests!**

---

### STEP 5: List Your Orders

View all your orders.

```
GET /api/v1/orders/
```

**Expected Response:**
```json
[
  {
    "id": "order-uuid",
    "status": "pending",
    "status_display": "Pending",
    "total_items": 2,
    "total_amount": "2400.00",
    "created_at": "2025-09-25T14:30:00Z",
    "updated_at": "2025-09-25T14:30:00Z"
  }
]
```

---

### STEP 6: Get Order Details

View specific order details.

```
GET /api/v1/orders/{order-id}/
```

**Replace `{order-id}` with actual order UUID**

**Expected Response:**
```json
{
  "id": "order-uuid",
  "user_email": "user@example.com",
  "status": "pending",
  "status_display": "Pending",
  "subtotal": "2400.00",
  "total_amount": "2400.00",
  "total_items": 2,
  "shipping_address": "123 Main Street",
  "shipping_city": "Kigali",
  "shipping_country": "Rwanda",
  "shipping_postal_code": "00100",
  "order_notes": "Please deliver after 5pm",
  "items": [
    {
      "id": "item-uuid",
      "product_id": "product-uuid",
      "product_name": "Laptop",
      "product_sku": "PRD-12345",
      "product_slug": "laptop",
      "quantity": 2,
      "unit_price": "1200.00",
      "subtotal": "2400.00",
      "created_at": "2025-09-25T14:30:00Z"
    }
  ],
  "created_at": "2025-09-25T14:30:00Z",
  "updated_at": "2025-09-25T14:30:00Z"
}
```

---

### STEP 7: Update Order Status (Admin Only)

**Requires admin/staff user!**

**Valid status transitions:**
- `pending` → `processing` or `cancelled`
- `processing` → `shipped` or `cancelled`
- `shipped` → `delivered` or `cancelled`
- `delivered` → (final, no changes)
- `cancelled` → (final, no changes)

**Request:**
```json
PATCH /api/v1/orders/{order-id}/status/

{
  "status": "processing"
}
```

**Expected Response:**
```json
{
  "message": "Order status updated to Processing",
  "status": "processing"
}
```

**Test all transitions:**
```json
// 1. Pending to Processing
{"status": "processing"}

// 2. Processing to Shipped
{"status": "shipped"}

// 3. Shipped to Delivered
{"status": "delivered"}
```

**Error cases:**
```json
// Invalid transition (shipped to pending)
{
  "status": ["Cannot change status from 'Shipped' to 'pending'"]
}

// Already delivered
{
  "status": ["Cannot change status from 'Delivered'"]
}
```

---

### STEP 8: Cancel Order (User)

Users can cancel their own orders (only pending/processing).

**Request:**
```json
PATCH /api/v1/orders/{order-id}/cancel/
```

**No body needed!**

**Expected Response:**
```json
{
  "message": "Order cancelled successfully",
  "order_id": "order-uuid",
  "status": "cancelled"
}
```

**What happens:**
- Order status changed to "cancelled"
- Product stock is restored
- Cannot cancel if order is shipped/delivered

**Error case (already shipped):**
```json
{
  "error": "Cannot cancel order with status: Shipped"
}
```

---

## Testing in Swagger UI

### 1. Authorize First
1. Click "Authorize" button (top right)
2. Enter: `Bearer your-access-token`
3. Click "Authorize"

### 2. Test Create Order
1. Ensure cart has items
2. Go to `POST /api/v1/orders/`
3. Click "Try it out"
4. Fill optional shipping details or leave empty `{}`
5. Click "Execute"
6. Copy order ID from response

### 3. Test Get Order Details
1. Go to `GET /api/v1/orders/{id}/`
2. Click "Try it out"
3. Paste order ID
4. Click "Execute"

### 4. Test Update Status (Admin)
1. Login as admin user
2. Re-authorize with admin token
3. Go to `PATCH /api/v1/orders/{id}/status/`
4. Enter: `{"status": "processing"}`
5. Click "Execute"

### 5. Test Cancel Order
1. Go to `PATCH /api/v1/orders/{id}/cancel/`
2. Click "Try it out"
3. Click "Execute" (no body needed)

---

## Testing with cURL

### Create Order:
```bash
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address": "123 Main St",
    "shipping_city": "Kigali",
    "shipping_country": "Rwanda"
  }'
```

### List Orders:
```bash
curl -X GET http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer your-token"
```

### Get Order Details:
```bash
curl -X GET http://localhost:8000/api/v1/orders/{order-id}/ \
  -H "Authorization: Bearer your-token"
```

### Update Status (Admin):
```bash
curl -X PATCH http://localhost:8000/api/v1/orders/{order-id}/status/ \
  -H "Authorization: Bearer admin-token" \
  -H "Content-Type: application/json" \
  -d '{"status": "processing"}'
```

### Cancel Order:
```bash
curl -X PATCH http://localhost:8000/api/v1/orders/{order-id}/cancel/ \
  -H "Authorization: Bearer your-token"
```

---

## Common Errors & Solutions

### Error: "Cart is empty"
**Solution:** Add items to cart first using `POST /api/v1/carts/`

### Error: "Insufficient stock"
**Solution:** Check product stock quantity, reduce order quantity

### Error: "Authentication credentials were not provided"
**Solution:** Add Authorization header: `Bearer your-token`

### Error: "Cannot cancel order with status: Delivered"
**Solution:** Only pending/processing orders can be cancelled

### Error: "Cannot change status from 'Delivered'"
**Solution:** Delivered is final state, create new order instead

### Error: 404 Not Found
**Solution:** Check order ID is correct and belongs to your user

### Error: 403 Forbidden (update status)
**Solution:** Only admin users can update order status

---

## Testing Checklist

```
□ Create products with stock
□ Add products to cart
□ View cart
□ Create order from cart
□ Verify cart is cleared
□ Verify stock reduced
□ List all orders
□ Get order details
□ Update status: pending → processing (admin)
□ Update status: processing → shipped (admin)
□ Update status: shipped → delivered (admin)
□ Cancel pending order (user)
□ Try cancelling delivered order (should fail)
□ Verify stock restored on cancellation
□ Try invalid status transition (should fail)
```

---

## Complete Test Scenario

**1. Setup:**
- Login as regular user
- Create product (admin) with stock=10

**2. Shopping Flow:**
- Add 2 items to cart
- View cart (total: 2 items)
- Create order
- Verify cart is empty
- Verify product stock reduced to 8

**3. Order Management:**
- List orders (see 1 order)
- Get order details
- Login as admin
- Update status to "processing"
- Update status to "shipped"
- Update status to "delivered"

**4. Cancellation Flow:**
- Create another order (2 items)
- Cancel order
- Verify stock restored to 10
- Try to cancel again (should fail)

**All APIs working correctly!**