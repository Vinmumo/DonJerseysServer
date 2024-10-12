from werkzeug.security import generate_password_hash
from myapp import create_app
from myapp.models import User, Category, Product, Order
from myapp.extensions import db

# Mock data
def seed_data():
    # Create admin and regular users
    users = [
        User(username="admin", email="admin@example.com", password_hash=generate_password_hash("admin123"), is_admin=True),
        User(username="john_doe", email="john@example.com", password_hash=generate_password_hash("password")),
        User(username="jane_doe", email="jane@example.com", password_hash=generate_password_hash("password")),
    ]

    # Add categories
    categories = [
        Category(name="Jerseys"),
        Category(name="Sportswear"),
        Category(name="Gym Equipment"),
    ]

    # Add products with mock image URLs
    products = [
        # Arsenal Jerseys
        Product(name="Arsenal Home Jersey 2024", description="Latest Arsenal home jersey.", price=1500, category_id=1, image_url="https://i1.adis.ws/i/ArsenalDirect/mit6141_f?&$plpImages$", stock=100),
        Product(name="Arsenal Away Jersey 2024", description="Latest Arsenal away jersey.", price=1500, category_id=1, image_url="https://i1.adis.ws/i/ArsenalDirect/mit6148_f?&$plpImages$", stock=80),
        Product(name="Arsenal Third Jersey 2024", description="Latest Arsenal third jersey.", price=1500, category_id=1, image_url="https://i1.adis.ws/i/ArsenalDirect/miz0114_f?&$plpImages$", stock=60),

        # Manchester United Jerseys
        Product(name="Man Utd Home Jersey 2024", description="Latest Manchester United home jersey.", price=1500, category_id=1, image_url="https://mufc-live.cdn.scayle.cloud/images/032465a23bed509d050589e6439809a2.jpg?brightness=1&width=720&height=960&quality=75&bg=ffffff", stock=90),
        Product(name="Man Utd Away Jersey 2024", description="Latest Manchester United away jersey.", price=1500, category_id=1, image_url="https://mufc-live.cdn.scayle.cloud/images/264a91ef570fbd6d9b401661e12cc1e7.jpg?brightness=1&width=720&height=960&quality=75&bg=ffffff", stock=70),
        Product(name="Man Utd Third Jersey 2024", description="Latest Manchester United third jersey.", price=1500, category_id=1, image_url="https://mufc-live.cdn.scayle.cloud/images/0a4f2b9bd692085741dfdaf2a1732efc.jpg?brightness=1&width=720&height=960&quality=75&bg=ffffff", stock=50),

        # Chelsea Jerseys
        Product(name="Chelsea Home Jersey 2024", description="Latest Chelsea home jersey.", price=1500, category_id=1, image_url="https://havencraft.co.ke/wp-content/uploads/2024/08/chelsea-nike-home-stadium-shirt-2024-25_ss5_p-200851164pv-2u-canixtzkdetrqr6ldmyhv-urvlapfisvffp6cea3w2-700x700-1.png", stock=100),
        Product(name="Chelsea Third Jersey 2024", description="Latest Chelsea away jersey.", price=1500, category_id=1, image_url="https://www.soccerlord.se/wp-content/uploads/2016/03/Chelsea-Third-Football-Shirt-24-25.jpg", stock=80),

        # Barcelona Jerseys
        Product(name="Barcelona Home Jersey 2024", description="Latest Barcelona home jersey.", price=1500, category_id=1, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTqhWo1_9LhNxXRSHdAJFODH0VsI0cluQjedkjIvSR6Ik5lqQXcfoO9GZQ3qCdHuu1sGAo&usqp=CAU", stock=100),
        Product(name="Barcelona Away Jersey 2024", description="Latest Barcelona away jersey.", price=1500, category_id=1, image_url="https://vintagejoint.co.za/cdn/shop/files/NYxIfgnR3wOCJTg.jpg?v=1725477625", stock=80),

        # Sportswear
        Product(name="Running Shoes", description="Comfortable running shoes.", price=2000, category_id=2, image_url="https://cdn.thewirecutter.com/wp-content/media/2023/09/running-shoes-2048px-5960.jpg", stock=200),
        Product(name="Yoga Pants", description="Flexible yoga pants.", price=750, category_id=2, image_url="https://images-na.ssl-images-amazon.com/images/I/41JkukHbj2L._UL500_.jpg", stock=120),
        Product(name="Cycling Shorts", description="Shorts designed for cycling.", price=2300, category_id=2, image_url="https://contents.mediadecathlon.com/p2464583/k$e441ddb57ab55a86c9a4a982d70fb756/essential-men-s-road-cycling-bibless-shorts.jpg?format=auto&quality=40&f=800x800", stock=100),
        Product(name="Boxing Gloves", description="High-quality boxing gloves.", price=7000, category_id=2, image_url="https://contents.mediadecathlon.com/p2604989/k$b5dee32969c43f9d5ee952e6b5222dc5/ergonomic-boxing-gloves-120-pink.jpg?format=auto&quality=40&f=800x800", stock=50),

        # Gym Equipment
        Product(name="Treadmill", description="Electric treadmill with multiple speed settings.", price=200000, category_id=3, image_url="https://contents.mediadecathlon.com/p2332850/k$19c2898171f7fdb9245f3c11c6f11532/t900a-treadmill.jpg?format=auto&quality=40&f=452x452", stock=10),
        Product(name="Dumbbells", description="Set of adjustable dumbbells.", price=20000, category_id=3, image_url="https://contents.mediadecathlon.com/p2297776/k$62dc0610d1672ffacd9da67f18a9f7a4/set-of-2-weight-training-dumbbells-10-kg.jpg?format=auto&quality=40&f=800x800", stock=100),
        Product(name="Resistance Bands", description="Durable resistance bands for workouts.", price=600, category_id=3, image_url="https://contents.mediadecathlon.com/p2041789/k$1c5cfd6465b59707399d7e5d7ae2ef14/resistance-band-cross-training-band-5-15-kg-red.jpg?format=auto&quality=40&f=452x452", stock=200),
    ]

    # Add users, categories, and products to the session
    db.session.bulk_save_objects(users)
    db.session.bulk_save_objects(categories)
    db.session.bulk_save_objects(products)
    
    # Commit to save data
    db.session.commit()

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_data()
