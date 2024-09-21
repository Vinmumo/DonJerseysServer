from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from myapp import create_app  # Import your app and db from your project
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

    # Add products 
    products = [
        Product(name="Arsenal Home Jersey", description="A high-quality football jersey.", price=1500, category_id=1, image_url="https://assets.adidas.com/images/w_1880,f_auto,q_auto/6b542a9c1b51491f9cdc9700fba1d7b3_9366/IT6140_HM30.jpg", stock=100),
        Product(name="Lakers Jersey", description="A durable basketball jersey.", price=1800, category_id=1, image_url="https://sportswardrobe.co.ke/wp-content/uploads/2020/10/LA-Lakers-kit-2020-A.png", stock=150),
        Product(name="Running Shoes", description="Comfortable running shoes.", price=2000, category_id=2, image_url="https://cdn.thewirecutter.com/wp-content/media/2023/09/running-shoes-2048px-5960.jpg", stock=200),
        Product(name="Yoga Pants", description="Flexible yoga pants.", price=750, category_id=2, image_url="https://contents.mediadecathlon.com/p1786632/k$33b35938871515cb720f0baadaed8f89/seamless-7slash8-dynamic-yoga-leggings-purple.jpg?format=auto&quality=40&f=800x800", stock=120),
        Product(name="Treadmill", description="Electric treadmill with multiple speed settings.", price=200000, category_id=3, image_url="https://contents.mediadecathlon.com/p2332850/k$19c2898171f7fdb9245f3c11c6f11532/t900a-treadmill.jpg?format=auto&quality=40&f=452x452", stock=10),
        Product(name="Dumbbells", description="Set of adjustable dumbbells.", price=20000, category_id=3, image_url="https://m.media-amazon.com/images/I/817AjxISeXL._AC_UF1000,1000_QL80_.jpg", stock=50),
        Product(name="Gym Mat", description="Non-slip gym mat.", price=5000, category_id=3, image_url="https://physioneeds.biz/wp-content/uploads/nc/s/i/sissel_gym_mat.jpg", stock=300),
        # Add more products here to reach 20
        Product(name="Cycling Shorts", description="Shorts designed for cycling.", price=2300, category_id=2, image_url="https://contents.mediadecathlon.com/p2464583/k$e441ddb57ab55a86c9a4a982d70fb756/essential-men-s-road-cycling-bibless-shorts.jpg?format=auto&quality=40&f=800x800", stock=100),
        Product(name="Weightlifting Gloves", description="Gloves for safe weightlifting.", price=4000, category_id=3, image_url="https://www.afrofit.co.ke/cdn/shop/products/41MPyrulzRL._AC_SY400_1200x1200.jpg?v=1590915705", stock=150),
        Product(name="Boxing Gloves", description="High-quality boxing gloves.", price=70000, category_id=2, image_url="https://www.sportsdirect.com/images/products/76233103_l.jpg", stock=50),
        Product(name="Sports Watch", description="Track your performance with this sports watch.", price=199.99, category_id=2, image_url="https://m.media-amazon.com/images/I/61iQ0vRLt7L._AC_SL1500_.jpg", stock=80),
        Product(name="Resistance Bands", description="Set of resistance bands for workouts.", price=12.99, category_id=3, image_url="https://contents.mediadecathlon.com/p1878175/k$2cc76a6ce0eaef29c03201c42e790f65/elastic-band-with-handles-tonetube-medium-resistance-5-kgslash10-lbs.jpg?format=auto&quality=40&f=800x800", stock=250),
        Product(name="Jump Rope", description="Speed jump rope.", price=9.99, category_id=3, image_url="https://cdn.shopify.com/s/files/1/1142/3440/products/muay-thai-20-heavy-pvc-jump-rope-elite-jumps-493334.jpg?v=1698144257", stock=500),
        Product(name="Soccer Ball", description="FIFA approved soccer ball.", price=24.99, category_id=1, image_url="https://ke.jumia.is/unsafe/fit-in/500x500/filters:fill(white)/product/84/9075231/1.jpg?9733", stock=300),
        Product(name="Baseball Bat", description="Aluminum baseball bat.", price=49.99, category_id=1, image_url="https://i5.walmartimages.com/asr/3ca86834-2713-44c3-a10a-1673832e71a6.128baedba5bd72004540e893656e79de.png?odnHeight=768&odnWidth=768&odnBg=FFFFFF", stock=70),
        Product(name="Tennis Racket", description="Lightweight tennis racket.", price=59.99, category_id=1, image_url="https://i5.walmartimages.com/seo/Wilson-Burn-Pink-25-in-Junior-Tennis-Racket-Ages-9-10_6f2317be-6133-4a23-8125-2ce46285260c.851da120f1cb97923c875bfb49af7f90.png", stock=100),
        Product(name="Golf Clubs", description="Full set of golf clubs.", price=499.99, category_id=1, image_url="https://www.collinsdictionary.com/images/full/golfclub_115180627_1000.jpg", stock=30),
        Product(name="Basketball", description="Indoor/outdoor basketball.", price=29.99, category_id=1, image_url="https://pimage.sport-thieme.com/facebook-open-graph/268-9119", stock=200),
        Product(name="Swimming Goggles", description="Anti-fog swimming goggles.", price=15.99, category_id=2, image_url="https://contents.mediadecathlon.com/p2189870/k$354d746c1870241031156d8d11f9d26f/swimming-goggles-100-xbase-size-l-black.jpg?format=auto&quality=40&f=800x800", stock=250),
        Product(name="Cricket Bat", description="Professional-grade cricket bat.", price=74.99, category_id=1, image_url="https://i5.walmartimages.com/asr/ba2d6248-935c-44da-814e-61e583b8aad7.4b38542ed84d1fcea038fea333602968.png", stock=60),
    ]

    # Add sample orders
    orders = [
        Order(user_id=2, product_id=1, quantity=2, status="completed", total_price=2 * 25.99),
        Order(user_id=3, product_id=5, quantity=1, status="pending", total_price=999.99),
    ]

    # Add all to session and commit to the database
    db.session.add_all(users)
    db.session.add_all(categories)
    db.session.add_all(products)
    db.session.add_all(orders)
    db.session.commit()

    print("Database seeded!")

if __name__ == "__main__":
    app = create_app() 
    with app.app_context():  
        seed_data()

