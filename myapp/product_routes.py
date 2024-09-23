from flask import Blueprint, jsonify, request, abort
from .models import Product, Category, db
from .utils import upload_image

product_bp = Blueprint('products', __name__)

# GET all products
# GET all products with support for 'limit' and 'sort'
@product_bp.route('/products', methods=['GET'])
def get_products():
    # Get query parameters for limit and sort
    limit = request.args.get('limit', default=6, type=int)  # Default limit of 6 products
    sort = request.args.get('sort', default='created_at_desc')  # Default sort by 'created_at' descending

    # Define sorting logic
    if sort == 'created_at_asc':
        sort_column = Product.created_at.asc()
    else:  # Default to descending
        sort_column = Product.created_at.desc()

    # Query the products, applying sorting and limiting the results
    products = Product.query.order_by(sort_column).limit(limit).all()

    # Return the product data
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
        "category": product.category,
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
    products = Product.query.filter_by(category_id=category_id).all()
    return jsonify([{
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'image_url': product.image_url
    } for product in products])

@product_bp.route('/upload', methods=['POST'])
def uploadd_image():
    image = request.files['file']
    result = upload_image(image)  
    if result:
        return jsonify(result), 200
    else:
        return jsonify({"error": "Image upload failed"}), 500