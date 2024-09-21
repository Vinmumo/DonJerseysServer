from flask import request, jsonify, Blueprint
from myapp.utils import upload_image
from myapp import db
from myapp.models import Product, Category

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/add_product', methods=['POST'])
def add_product():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400

    image = request.files['image']
    name = request.form['name']
    description = request.form['description']
    price = float(request.form['price'])
    category_id = int(request.form['category_id'])
    stock = int(request.form['stock'])

    # Upload image to Cloudinary
    upload_result = upload_image(image)
    if not upload_result:
        return jsonify({'error': 'Image upload failed'}), 500

    # Save the product with image URL
    new_product = Product(
        name=name,
        description=description,
        price=price,
        category_id=category_id,
        image_url=upload_result['url'],
        stock=stock
    )
    
    db.session.add(new_product)
    db.session.commit()

    return jsonify({'message': 'Product added successfully!'}), 201
