from flask import Blueprint, jsonify, request, abort
from .models import Product, Category, Order, db
from .utils import upload_image
from datetime import datetime
import requests
import base64
import os

product_bp = Blueprint('products', __name__)

# GET all products

@product_bp.route('/products', methods=['GET'])
def get_products():
    # Get query parameters for limit and sort
    limit = request.args.get('limit', type=int)  # Optional limit
    sort = request.args.get('sort', default='created_at_desc')  # Default sort by 'created_at' descending

    # Define sorting logic
    if sort == 'created_at_asc':
        sort_column = Product.created_at.asc()
    else:  # Default to descending
        sort_column = Product.created_at.desc()

    # Query the products, applying sorting
    query = Product.query.order_by(sort_column)
    
    # Apply limit if provided
    if limit:
        query = query.limit(limit)

    products = query.all()

    return jsonify([{
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "category_id": product.category_id, 
        "category": product.category.name,  
        "stock": product.stock,
        "image_url": product.image_url
    } for product in products])

# GET a single product by ID
@product_bp.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "category": {
            "id": product.category.id,  
            "name": product.category.name
        },
        "stock": product.stock,
        "image_url": product.image_url
    })
# POST a new product
@product_bp.route('/products', methods=['POST'])
def add_product():
    data = request.json
    new_product = Product(
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        category_id=data['category_id'],
        stock=data.get('stock', 0),
        image_url=data.get('imageUrl')  
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({
        "message": "Product added successfully!",
        "product": new_product.id
    }), 201

# PUT (update) an existing product
@product_bp.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.json
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.category = data.get('category', product.category)
    product.stock = data.get('stock', product.stock)
    product.image_url = data.get('image_url', product.image_url)

    db.session.commit()
    return jsonify({"message": "Product updated successfully!"})

# DELETE a product
@product_bp.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully!"})

# Count products by category
@product_bp.route('/products/count-by-category', methods=['GET'])
def count_products_by_category():
    categories = db.session.query(
        Category.name, 
        Category.id, 
        db.func.count(Product.id).label('count')
    ).join(Product).group_by(Category.id).all()

    return jsonify([{
        'category_name': category.name,
        'category_id': category.id,
        'count': category.count
    } for category in categories])

@product_bp.route('/products/by-category/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    # Add query parameters for limit and sort
    limit = request.args.get('limit', default=6, type=int)
    sort = request.args.get('sort', default='created_at_desc')

    # Define sorting logic
    if sort == 'created_at_asc':
        sort_column = Product.created_at.asc()
    else:
        sort_column = Product.created_at.desc()

    # Query products filtered by category, sorted, and limited
    products = Product.query.filter_by(category_id=category_id).order_by(sort_column).limit(limit).all()

    return jsonify([{
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'image_url': product.image_url
    } for product in products])

@product_bp.route('/upload', methods=['POST'])
def upload_image():
    image = request.files['file']
    result = upload_image(image)
    
    if result:
        return jsonify({'image_url': result['url']}), 200
    else:
        return jsonify({"error": "Image upload failed"}), 500



@product_bp.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    cart = data.get('cart', [])
    delivery_details = data.get('delivery_details', {})

    if not cart:
        return jsonify({'success': False, 'message': 'Cart is empty.'})

    if not delivery_details:
        return jsonify({'success': False, 'message': 'Delivery details are required.'})

    # Validate delivery details
    name = delivery_details.get('name')
    email = delivery_details.get('email')
    phone = delivery_details.get('phone')
    location = delivery_details.get('location')

    if not all([name, email, phone, location]):
        return jsonify({'success': False, 'message': 'All delivery details are required.'})

    order_items = []
    total_price = 0

    for item in cart:
        product = Product.query.get(item['id'])
        if not product or item['quantity'] > product.stock:
            return jsonify({'success': False, 'message': f'Insufficient stock for {item["name"]}'})
        
        # Create order items
        order = Order(
            product_id=item['id'],
            name=name,
            email=email,
            phone=phone,
            location=location,
            quantity=item['quantity'],
            total_price=item['quantity'] * product.price
        )
        order_items.append(order)

        # Update stock
        product.stock -= item['quantity']
        total_price += item['quantity'] * product.price

    # Commit all orders and stock changes
    db.session.add_all(order_items)
    db.session.commit()

    # Initiate M-Pesa payment
    mpesa_payment_response = initiate_mpesa_payment(phone, total_price)
    
    if mpesa_payment_response['success']:
        return jsonify({'success': True, 'message': 'Order placed and payment successful!'})
    else:
        return jsonify({'success': False, 'message': 'Payment failed. Try again.'})


# Function to initiate M-Pesa STK Push
def initiate_mpesa_payment(phone, total_price):
    shortcode = os.getenv('MPESA_SHORTCODE')
    passkey = os.getenv('MPESA_PASSKEY')
    consumer_key = os.getenv('MPESA_CONSUMER_KEY')
    consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
    environment = os.getenv('MPESA_ENVIRONMENT', 'sandbox')

    # Step 1: Get access token
    access_token = get_mpesa_access_token(consumer_key, consumer_secret, environment)
    if not access_token:
        return {'success': False, 'message': 'Failed to get access token.'}

    # Step 2: Prepare the password and timestamp for the request
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(shortcode.encode('utf-8') + passkey.encode('utf-8') + timestamp.encode('utf-8')).decode('utf-8')

    # Step 3: Prepare STK Push request body
    stk_push_url = f'https://{environment}.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    body = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerBuyGoodsOnline",  # For Buy Goods and Services
        "Amount": total_price,
        "PartyA": phone,  # Customer phone number
        "PartyB": shortcode,  # Your till number
        "PhoneNumber": phone,  # Same customer phone number
        "CallBackURL": "https://df84-102-210-25-54.ngrok-free.app//mpesa/callback",
        "AccountReference": "Order Payment",
        "TransactionDesc": "Payment for Order"
    }

    # Step 4: Send the STK Push request
    response = requests.post(stk_push_url, json=body, headers=headers)
    response_data = response.json()

    if response.status_code == 200 and response_data.get('ResponseCode') == '0':
        return {'success': True, 'message': 'STK Push sent successfully'}
    else:
        return {'success': False, 'message': 'STK Push request failed.'}


# Function to get M-Pesa access token
def get_mpesa_access_token(consumer_key, consumer_secret, environment):
    auth_url = f'https://{environment}.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(auth_url, auth=(consumer_key, consumer_secret))

    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        return None
    

@product_bp.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    data = request.json

    # Safaricom sends the transaction details in the 'Body'
    result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
    result_desc = data.get('Body', {}).get('stkCallback', {}).get('ResultDesc')
    merchant_request_id = data.get('Body', {}).get('stkCallback', {}).get('MerchantRequestID')
    checkout_request_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')

    # Process the callback based on the result
    if result_code == 0:
        # Payment successful
        # You can mark the order as paid in your database or handle further logic
        return jsonify({'success': True, 'message': 'Payment successful.'})
    else:
        # Payment failed
        # Log the failure or notify the user
        return jsonify({'success': False, 'message': f'Payment failed: {result_desc}.'})