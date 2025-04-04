from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'snapcart-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///snapcart.db'
db = SQLAlchemy(app)

# User model    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Dummy product data
products = [
    {'id': 1, 'name': 'Smartphone', 'price': 15000, "url":"\static\images\Galaxy-S21-Ultra.webp" },
    {'id': 2, 'name': 'Headphones', 'price': 1200, "url":"\static\images\headphones.webp"},
    {'id': 3, 'name': 'Keyboard', 'price': 800, "url":"\static\images\keyboard.jpeg"}
]

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'user' not in session:
        flash("Please login to add items to your cart.")
        return redirect(url_for('login'))

    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        # Get existing cart or empty list
        cart = session.get('cart', [])
        cart.append(product)
        session['cart'] = cart  # Save updated cart back to session
        flash(f"{product['name']} added to cart.")
    else:
        flash("Product not found.")
        
    return redirect(url_for('index'))




@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total = sum(item['price'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('cart'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user'] = user.email
            return redirect('/')
        flash("Invalid credentials!")
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash("Email already exists!")
            return redirect('/signup')
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful! Please login.")
        return redirect('/login')
    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('cart', None)
    return redirect('/')
