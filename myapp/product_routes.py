from flask import Blueprint, jsonify, request, abort
from .models import Product, Category, Order, OrderItem ,db
from .utils import upload_image
from datetime import datetime
from dotenv import load_dotenv
import requests
import base64
import os

load_dotenv()

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
        db.func.coalesce(db.func.count(Product.id), 0).label('count')
    ).outerjoin(Product).group_by(Category.id).all()

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
def upload_image_route():  
    image = request.files.get('file')
    if image:
        result = upload_image(image)
        if result:
            return jsonify({'image_url': result['url']}), 200
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

    total_price = 0
    order_items = []

    # Create the main order record
    order = Order(
        user_id=None,  # Optional if not requiring login
        name=name,
        email=email,
        phone=phone,
        location=location,
        total_price=0,  # Will update after calculating total
        payment_status='Pending'
    )

    # Process each cart item
    for item in cart:
        product = Product.query.get(item['product_id'])
        if not product or item['quantity'] > product.stock:
            return jsonify({'success': False, 'message': f'Insufficient stock for {item["product_id"]}'})
        
        # Create an OrderItem for each product in the cart
        order_item = OrderItem(
            product_id=item['product_id'],
            quantity=item['quantity'],
            unit_price=product.price
        )
        order_items.append(order_item)

        # Update stock and total price
        product.stock -= item['quantity']
        total_price += item['quantity'] * product.price

    # Add order items to the order
    order.items.extend(order_items)
    order.total_price = total_price  

    # Save everything to the database
    db.session.add(order)
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
    
    recipient_phone_number = os.getenv('MY_PHONE_NUMBER')  # Ensure this is set in your environment variables

    # Step 1: Get access token
    access_token = get_mpesa_access_token()
    print("Access Token:", access_token)  # Debugging access token
    if not access_token:
        return {'success': False, 'message': 'Failed to get access token.'}

    # Step 2: Prepare the password and timestamp for the request
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((shortcode + passkey + timestamp).encode()).decode('utf-8')

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
        "TransactionType": "CustomerPayBillOnline", 
        "Amount": total_price,
        "PartyA": phone,  
        "PartyB": shortcode,  
        "PhoneNumber": phone, 
        "CallBackURL": "https://f989-102-210-25-54.ngrok-free.app/mpesa/callback",
        "AccountReference": "Order Payment",
        "TransactionDesc": "Payment for Order"
    }

    # Step 4: Send the STK Push request
    response = requests.post(stk_push_url, json=body, headers=headers)
    response_data = response.json()
    print("STK Push Response:", response_data)  # Debugging response data

    if response.status_code == 200 and response_data.get('ResponseCode') == '0':
        return {'success': True, 'message': 'STK Push sent successfully'}
    else:
        return {'success': False, 'message': 'STK Push request failed.', 'details': response_data}


# Function to get M-Pesa access token
def get_mpesa_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    consumer_key = os.getenv("MPESA_CONSUMER_KEY")
    consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")

    if not consumer_key or not consumer_secret:
        print("Error: Missing M-Pesa consumer key or secret.")
        return None

    # Encode key and secret to base64
    auth_string = f"{consumer_key}:{consumer_secret}"
    auth_header = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print("Response Status:", response.status_code)
            print("Response Body:", response.text)
            return None
    except requests.RequestException as e:
        print("Request error:", e)
        return None

@product_bp.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    data = request.json
    result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
    result_desc = data.get('Body', {}).get('stkCallback', {}).get('ResultDesc')
    checkout_request_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
    
    # Example: Retrieve order by checkout_request_id if stored in Order table
    order = Order.query.filter_by(checkout_request_id=checkout_request_id).first()

    if order:
        if result_code == 0:
            # Payment successful
            order.payment_status = 'Completed'
            db.session.commit()
            return jsonify({'success': True, 'message': 'Payment successful.'})
        else:
            # Payment failed
            order.payment_status = 'Failed'
            db.session.commit()
            return jsonify({'success': False, 'message': f'Payment failed: {result_desc}.'})
    else:
        return jsonify({'success': False, 'message': 'Order not found.'}), 404

    

@product_bp.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'GET':
        # Fetch all categories
        categories = Category.query.all()
        return jsonify([{
            'id': category.id,
            'name': category.name
        } for category in categories]), 200

    elif request.method == 'POST':
        # Add a new category
        if not request.json or not 'name' in request.json:
            return jsonify({'error': 'Category name is required'}), 400

        category_name = request.json['name']
        new_category = Category(name=category_name)

        try:
            db.session.add(new_category)
            db.session.commit()
            return jsonify({'message': 'Category added successfully'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        

token = get_mpesa_access_token()
print("Access Token:", token)
