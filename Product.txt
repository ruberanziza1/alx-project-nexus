# Complete API Testing Guide - Products API

## 📋 Prerequisites Setup

### 1. Start Your Server
```bash
python manage.py runserver
```

Your API will be available at: `http://localhost:8000`

### 2. Get Authentication Token (If Required)

```bash
# Login to get token
POST http://localhost:8000/api/v1/auth/login/

{
  "email": "admin@example.com",
  "password": "your-password"
}

# Response:
{
  "access": "your-access-token-here",
  "refresh": "your-refresh-token-here"
}
```

Copy the `access` token - you'll need it for creating/updating products.

---

## 🧪 Testing Methods

### Method 1: Using Swagger UI (Easiest!)

1. **Open Swagger**: `http://localhost:8000/api/schema/swagger-ui/`
2. **Authorize** (if needed): Click "Authorize" button, paste token: `Bearer your-token`
3. **Test APIs** directly in browser

### Method 2: Using Postman

Download Postman: https://www.postman.com/downloads/

### Method 3: Using cURL (Command Line)

Works in terminal/PowerShell

---

## 🎯 Test Scenarios (Step by Step)

## **STEP 1: List All Products (Public - No Auth Needed)**

### Swagger:
1. Go to `GET /api/v1/products/`
2. Click "Try it out"
3. Click "Execute"

### Postman:
```
Method: GET
URL: http://localhost:8000/api/v1/products/
Headers: (none needed)
```

### cURL:
```bash
curl -X GET http://localhost:8000/api/v1/products/
```

### Expected Response:
```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```

*(Empty because no products yet)*

---

## **STEP 2: Create Your First Product (Admin Auth Required)**

### Swagger:
1. Go to `POST /api/v1/products/`
2. Click "Try it out"
3. **Click "Authorize"** → Enter: `Bearer your-access-token`
4. Fill in the request body:

```json
{
  "name": "Gaming Laptop",
  "description": "High performance gaming laptop with RTX 4080 GPU, 32GB RAM",
  "short_description": "Best gaming laptop 2025",
  "price": 1299.99,
  "compare_price": 1499.99,
  "stock_quantity": 50,
  "low_stock_threshold": 10,
  "category": "Electronics",
  "is_featured": true,
  "is_active": true
}
```

5. Click "Execute"

### Postman:
```
Method: POST
URL: http://localhost:8000/api/v1/products/

Headers:
- Authorization: Bearer your-access-token
- Content-Type: application/json

Body (raw JSON):
{
  "name": "Gaming Laptop",
  "description": "High performance gaming laptop with RTX 4080 GPU, 32GB RAM",
  "short_description": "Best gaming laptop 2025",
  "price": 1299.99,
  "compare_price": 1499.99,
  "stock_quantity": 50,
  "low_stock_threshold": 10,
  "category": "Electronics",
  "is_featured": true,
  "is_active": true
}
```

### cURL:
```bash
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gaming Laptop",
    "description": "High performance gaming laptop with RTX 4080 GPU",
    "price": 1299.99,
    "category": "Electronics",
    "stock_quantity": 50
  }'
```

### Expected Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Gaming Laptop",
  "slug": "gaming-laptop",
  "description": "High performance gaming laptop with RTX 4080 GPU, 32GB RAM",
  "short_description": "Best gaming laptop 2025",
  "price": "1299.99",
  "compare_price": "1499.99",
  "sku": "PRD-550E8400",
  "stock_quantity": 50,
  "low_stock_threshold": 10,
  "category": "Electronics",
  "is_active": true,
  "is_featured": true,
  "created_at": "2025-09-25T10:30:00Z",
  "updated_at": "2025-09-25T10:30:00Z"
}
```

✅ **Copy the `id` value** - you'll need it for next tests!

---

## **STEP 3: Create Product with Images**

### Swagger:
1. Go to `POST /api/v1/products/`
2. Click "Try it out"
3. **Change Content-Type** to `multipart/form-data` (automatic when you add files)
4. Fill form fields:
   - name: Gaming Mouse
   - description: RGB gaming mouse
   - price: 79.99
   - category: Electronics
   - stock_quantity: 100
5. **Click "Choose Files"** for `images` field
6. Select 1-5 image files (jpg, png, webp)
7. Click "Execute"

### Postman:
```
Method: POST
URL: http://localhost:8000/api/v1/products/

Headers:
- Authorization: Bearer your-access-token

Body (form-data):
- name: Gaming Mouse
- description: RGB gaming mouse with 16000 DPI
- price: 79.99
- category: Electronics
- stock_quantity: 100
- images: [Click "File" and select image1.jpg]
- images: [Click "File" and select image2.jpg]
```

**Important**: Add multiple `images` keys with same name for multiple images!

### cURL:
```bash
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer your-token" \
  -F "name=Gaming Mouse" \
  -F "description=RGB gaming mouse with 16000 DPI" \
  -F "price=79.99" \
  -F "category=Electronics" \
  -F "stock_quantity=100" \
  -F "images=@/path/to/image1.jpg" \
  -F "images=@/path/to/image2.jpg"
```

### Expected Response:
```json
{
  "id": "product-uuid",
  "name": "Gaming Mouse",
  "category": "Electronics",
  "price": "79.99",
  "images": [
    {
      "id": "image-uuid-1",
      "image": "/media/products/image1.jpg",
      "image_url": "http://localhost:8000/media/products/image1.jpg",
      "is_primary": true
    }
  ]
}
```

---

## **STEP 4: Get Single Product Details**

Use the product ID from Step 2 or 3.

### Swagger:
1. Go to `GET /api/v1/products/{id}/`
2. Click "Try it out"
3. Enter product ID: `550e8400-e29b-41d4-a716-446655440000`
4. Click "Execute"

### Postman:
```
Method: GET
URL: http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000/
Headers: (none needed)
```

### cURL:
```bash
curl -X GET http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000/
```

### Expected Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Gaming Laptop",
  "slug": "gaming-laptop",
  "description": "High performance gaming laptop with RTX 4080 GPU, 32GB RAM",
  "price": "1299.99",
  "compare_price": "1499.99",
  "category": "Electronics",
  "images": [...],
  "stock_status": "in_stock",
  "discount_percentage": 13.34,
  "is_on_sale": true
}
```

---

## **STEP 5: Filter Products by Category**

### Swagger:
1. Go to `GET /api/v1/products/`
2. Click "Try it out"
3. Add query parameter: `category=Electronics`
4. Click "Execute"

### Postman:
```
Method: GET
URL: http://localhost:8000/api/v1/products/?category=Electronics
```

### cURL:
```bash
curl -X GET "http://localhost:8000/api/v1/products/?category=Electronics"
```

### Expected Response:
```json
{
  "count": 2,
  "results": [
    {
      "id": "...",
      "name": "Gaming Laptop",
      "category": "Electronics"
    },
    {
      "id": "...",
      "name": "Gaming Mouse",
      "category": "Electronics"
    }
  ]
}
```

---

## **STEP 6: Search Products**

### Test Search:
```
GET /api/v1/products/?search=gaming
```

Searches in: name, description, sku, category

### Postman:
```
Method: GET
URL: http://localhost:8000/api/v1/products/?search=gaming
```

### Expected Response:
Returns all products with "gaming" in name/description/category

---

## **STEP 7: Filter by Price Range**

### Swagger/Postman:
```
GET /api/v1/products/?min_price=50&max_price=1000
```

### cURL:
```bash
curl -X GET "http://localhost:8000/api/v1/products/?min_price=50&max_price=1000"
```

---

## **STEP 8: Get Only In-Stock Products**

```
GET /api/v1/products/?in_stock=true
```

---

## **STEP 9: Get Featured Products**

```
GET /api/v1/products/?is_featured=true
```

---

## **STEP 10: Combined Filters**

```
GET /api/v1/products/?category=Electronics&min_price=500&in_stock=true&is_featured=true
```

---

## **STEP 11: Update Product (Partial Update)**

### Swagger:
1. Go to `PATCH /api/v1/products/{id}/`
2. Click "Try it out"
3. **Authorize** with token
4. Enter product ID
5. Update body (only fields you want to change):

```json
{
  "price": 1199.99,
  "stock_quantity": 45
}
```

6. Click "Execute"

### Postman:
```
Method: PATCH
URL: http://localhost:8000/api/v1/products/product-id-here/

Headers:
- Authorization: Bearer your-token
- Content-Type: application/json

Body:
{
  "price": 1199.99,
  "stock_quantity": 45
}
```

### cURL:
```bash
curl -X PATCH http://localhost:8000/api/v1/products/product-id-here/ \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"price": 1199.99}'
```

---

## **STEP 12: Update Product Category**

```json
PATCH /api/v1/products/{id}/

{
  "category": "Gaming Laptops"
}
```

---

## **STEP 13: Add More Images to Existing Product**

### Postman:
```
Method: PATCH
URL: http://localhost:8000/api/v1/products/product-id-here/

Headers:
- Authorization: Bearer your-token

Body (form-data):
- images: [Select new image file]
```

New images will be added (old images preserved).

---

## **STEP 14: Delete Product (Soft Delete)**

### Swagger:
1. Go to `DELETE /api/v1/products/{id}/`
2. Click "Try it out"
3. **Authorize** with token
4. Enter product ID
5. Click "Execute"

### Postman:
```
Method: DELETE
URL: http://localhost:8000/api/v1/products/product-id-here/

Headers:
- Authorization: Bearer your-token
```

### cURL:
```bash
curl -X DELETE http://localhost:8000/api/v1/products/product-id-here/ \
  -H "Authorization: Bearer your-token"
```

Product will be soft-deleted (is_active=False).

---

## **STEP 15: Create Multiple Products (Different Categories)**

Create these products to test filtering:

### Product 1: Book
```json
{
  "name": "Python Programming",
  "description": "Learn Python programming from scratch",
  "price": 49.99,
  "category": "Books",
  "stock_quantity": 200
}
```

### Product 2: Clothing
```json
{
  "name": "Gaming T-Shirt",
  "description": "Cool gaming t-shirt",
  "price": 25.99,
  "category": "Clothing",
  "stock_quantity": 150
}
```

### Product 3: Sports
```json
{
  "name": "Tennis Racket",
  "description": "Professional tennis racket",
  "price": 129.99,
  "category": "Sports",
  "stock_quantity": 30
}
```

---

## 🔍 Advanced Testing Scenarios

### Scenario 1: Pagination
```
GET /api/v1/products/?page=1
GET /api/v1/products/?page=2
```

### Scenario 2: Sorting
```
GET /api/v1/products/?ordering=price          # Low to high
GET /api/v1/products/?ordering=-price         # High to low
GET /api/v1/products/?ordering=name           # A-Z
GET /api/v1/products/?ordering=-created_at    # Newest first
```

### Scenario 3: Complex Query
```
GET /api/v1/products/?category=Electronics&min_price=500&max_price=2000&search=gaming&is_featured=true&in_stock=true&ordering=-price
```

---

## ✅ Expected Results Checklist

After testing, you should see:

- ✅ List empty products initially
- ✅ Create product successfully
- ✅ Product has auto-generated slug and SKU
- ✅ Upload images and get URLs back
- ✅ Filter by category works
- ✅ Search works across name/description/category
- ✅ Price range filtering works
- ✅ Stock filtering works
- ✅ Update product fields
- ✅ Add more images to existing product
- ✅ Delete product (soft delete)
- ✅ Image URLs are accessible

---

## 🐛 Common Issues & Solutions

### Issue 1: "Authentication credentials were not provided"
**Solution**: Add Authorization header: `Bearer your-token`

### Issue 2: Images not uploading
**Solution**: 
- Use `multipart/form-data` content type
- In Postman: Use "form-data" body type
- Select "File" type for images field

### Issue 3: Category validation error
**Solution**: Category must be 2-100 characters, will auto-format to Title Case

### Issue 4: Price validation error
**Solution**: Price must be > 0 and max 2 decimal places

### Issue 5: Image URL returns 404
**Solution**: 
- Check MEDIA_URL in settings.py
- Check urls.py has media URL configuration
- Check media folder permissions

### Issue 6: "Product with this name already exists"
**Solution**: Product names must be unique, use different name

---

## 📊 Testing Checklist

Copy this checklist:

```
□ Start server successfully
□ Access Swagger UI
□ Get authentication token
□ List products (empty)
□ Create product without images
□ Create product with images
□ View single product
□ Filter by category
□ Search products
□ Filter by price range
□ Filter in-stock products
□ Get featured products
□ Update product price
□ Update product category
□ Add more images
□ Delete product
□ Test pagination
□ Test sorting
□ Test complex filters
□ Verify image URLs work
```

---

## 🎉 Success Indicators

Your API is working perfectly if:

1. ✅ All CRUD operations work
2. ✅ Images upload and URLs are returned
3. ✅ Filtering by category works
4. ✅ Search finds products
5. ✅ Price/stock filters work
6. ✅ Authentication required for admin actions
7. ✅ Validation errors show helpful messages
8. ✅ Image URLs are accessible in browser
9. ✅ Category auto-formats to Title Case
10. ✅ Soft delete works (is_active=False)

---

## 📝 Quick Test Script (Copy & Paste)

```bash
# 1. List products
curl http://localhost:8000/api/v1/products/

# 2. Create product (replace YOUR_TOKEN)
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "description": "Test description",
    "price": 99.99,
    "category": "Electronics",
    "stock_quantity": 50
  }'

# 3. Filter by category
curl "http://localhost:8000/api/v1/products/?category=Electronics"

# 4. Search
curl "http://localhost:8000/api/v1/products/?search=test"
```

**Now start testing! Good luck! 🚀**