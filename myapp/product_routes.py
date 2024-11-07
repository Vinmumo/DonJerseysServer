from flask import Blueprint, jsonify, request, abort
from .models import Product, Category, Order, OrderItem ,db
from .utils import upload_image
from datetime import datetime
from dotenv import load_dotenv
import json
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
    
    # Directly assign sizes if it's already a list
    sizes = product.sizes if product.sizes else []
    
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
        "image_url": product.image_url,
        "sizes": sizes  # Include sizes in the response
    })


# POST a new product
@product_bp.route('/products', methods=['POST'])
def add_product():
    data = request.json
    
    # Check if sizes is a list; if so, use it directly. Otherwise, split it.
    sizes = data.get('sizes', [])
    if isinstance(sizes, str):
        sizes = [size.strip() for size in sizes.split(',') if size.strip()]
    elif isinstance(sizes, list):
        sizes = [size.strip() for size in sizes if size.strip()]
    
    # Convert list to JSON string
    sizes_json = json.dumps(sizes)

    new_product = Product(
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        category_id=data['category_id'],
        stock=data.get('stock', 0),
        image_url=data.get('imageUrl'),
        sizes=sizes_json  # Store JSON-encoded sizes
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
    total_price = data.get('total_price', 0)

    if not cart or not delivery_details:
        return jsonify({'success': False, 'message': 'Cart or delivery details are missing.'}), 400

    # Extract delivery details
    name = delivery_details.get('name')
    email = delivery_details.get('email')
    phone = delivery_details.get('phone')
    location = delivery_details.get('location')

    if not all([name, phone, location]):
        return jsonify({'success': False, 'message': 'All delivery details are required.'}), 400

    # Create an Order instance with the total price from frontend
    order = Order(
        user_id=None,
        name=name,
        email=email,
        phone=phone,
        location=location,
        total_price=total_price,
        payment_status='Payment on Delivery'
    )
    db.session.add(order)
    db.session.commit()

    # Add each item as an OrderItem linked to the Order
    order_items = []
    for item in cart:
        product = Product.query.get(item['id'])
        if not product:
            return jsonify({'success': False, 'message': f"Product with ID {item['id']} not found."}), 404
        if item['quantity'] > product.stock:
            return jsonify({'success': False, 'message': f"Quantity for {product.name} exceeds stock."}), 400

        order_items.append(OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item['quantity'],
            unit_price=product.price,
            size=item.get('size')
        ))

    db.session.bulk_save_objects(order_items)
    db.session.commit()

    return jsonify({'success': True, 'order_id': order.id}), 201




# Function to initiate M-Pesa STK Push
def initiate_mpesa_payment(phone, total_price):
    shortcode = str(174379)
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
    password = base64.b64encode((shortcode + timestamp).encode()).decode('utf-8')

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
        "CallBackURL": "https://bdfb-102-210-25-54.ngrok-free.app/mpesa/callback",
        "AccountReference": "Order Payment",
        "TransactionDesc": "Payment for Order"
    }

    # Step 4: Send the STK Push request
    response = requests.post(stk_push_url, json=body, headers=headers)
    response_data = response.json()
    print("STK Push Response:", response_data)  # Debugging response data

    if response.status_code == 200 and response_data.get('ResponseCode') == '0':
        return {
            'success': True,
            'message': 'STK Push sent successfully',
            'checkout_request_id': response_data.get('CheckoutRequestID')
        }
    else:
        return {
            'success': False,
            'message': 'STK Push request failed.',
            'details': response_data
        }


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


@product_bp.route('/getorders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    orders_data = [
        {
            "id": order.id,
            "user": {
                "username": order.user.username if order.user else "Guest",
                "email": order.user.email if order.user else order.email  # Fallback to order email if no user is linked
            },
            "name": order.name,
            "phone": order.phone,
            "location": order.location,
            "total_price": order.total_price,
            "order_date": order.order_date.isoformat(),
            "payment_status": order.payment_status,
            "order_items": [
                {
                    "product_name": item.product.name,
                    "description": item.product.description,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "size": item.size,
                    "total_item_price": item.quantity * item.unit_price
                }
                for item in order.items  # Using the 'items' relationship in the Order model
            ]
        }
        for order in orders
    ]
    return jsonify(orders_data)


        

token = get_mpesa_access_token()
print("Access Token:", token)
