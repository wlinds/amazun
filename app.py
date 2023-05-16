from models import *
import os, secrets, store_manager, books, customer
from Scripts.utils import titles_by_author, get_title, total_sales, welcome_message, drop_table
from flask import Flask, render_template, request, redirect, session, current_app, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

database_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'amazun.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(256))

    def set_password(self, password):
        self.password = generate_password_hash(password)  # Update this line

    def check_password(self, password):
        return check_password_hash(self.password, password)

def create_user(username, password):
     #TODO: existing user exception handling (caused by unique constraint)
    with current_app.app_context():
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user is not None and user.check_password(password):
            flash('Successful authentication')
            session['user_id'] = user.id
            session['username'] = user.username
            
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/dashboard')
def dashboard():
    # Access the user session
    user_id = session.get('user_id')
    username = session.get('username')

    if user_id:
        welcome = welcome_message(username)
        return render_template('dashboard.html', greeting=welcome)
    else:
        # User is not authenticated, redirect
        return redirect(url_for('login'))

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if request.method == 'POST':
        selected_isbn = request.form.get('isbn')
        selected_store_id = request.form.get('store_id')
        selected_quantity = request.form.get('quantity')

        # Call add_to_inventory()
        store_manager.add_to_inventory(selected_isbn, selected_store_id, int(selected_quantity), verbose=True)

    inventory_table = db.session.query(Inventory).all()

    session = Session()

    all_books = session.query(Books).all()
    books_data = [{'isbn': book.isbn13, 'title': book.title} for book in all_books]

    stores = session.query(Store).all()
    stores_data = [{'id': store.id, 'name': store.store_name} for store in stores]

    session.close()

    return render_template('inventory.html',
                           results=inventory_table,
                           books=books_data,
                           stores=stores_data)

@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if request.method == 'POST':
        selected_isbn = request.form.get('isbn')
        selected_store_id = request.form.get('store_id')
        selected_customer_id = request.form.get('customer_id')
        selected_quantity = request.form.get('quantity')

        # Call purchase_book()
        customer.purchase_book(selected_isbn, selected_store_id, selected_customer_id, int(selected_quantity))

    transaction_table = db.session.query(Transaction).all()
    sales_info = total_sales()

    session = Session()

    # Get drop down data for customer, books and stores
    books = session.query(Books).all()
    books_data = [{'isbn': book.isbn13, 'title': book.title} for book in books]

    stores = session.query(Store).all()
    stores_data = [{'id': store.id, 'name': store.store_name} for store in stores]

    customers = session.query(Customer).all()
    customers_data = [{'id': customer.ID, 'name': customer.name} for customer in customers]

    session.close()

    return render_template('transactions.html',
                           results=transaction_table,
                           total_sales=sales_info,
                           books=books_data,
                           stores=stores_data,
                           customers=customers_data)

@app.route('/customers', methods=['GET', 'POST'])
def customers():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        zipcode = request.form.get('zipcode')
        email = request.form.get('email')

        customer.new_customer(name, surname, address, city, state, zipcode, email, verbose=True)

    customer_table = db.session.query(Customer).all()

    return render_template('customers.html',
                           results=customer_table)

@app.route('/delete_customer', methods=['POST'])
def delete_customer():
    customer_id = request.form.get('customer_id')
    print(f"Customer ID: {customer_id}")
    customer.remove_customer(customer_id, verbose=True)

    # Redirect to after deletion
    return redirect('/customers')

@app.route('/authors', methods=['GET', 'POST'])
def authors():
    sort_by = request.args.get('sort_by')  # Get the sorting parameter from the query string

    # Retrieve the author table from the database
    author_table = db.session.query(Author)

    # Apply sorting based on the selected parameter
    if sort_by == 'id':
        author_table = author_table.order_by(Author.ID)
    elif sort_by == 'name':
        author_table = author_table.order_by(Author.name)
    elif sort_by == 'birthdate':
        author_table = author_table.order_by(Author.birthdate)

    # Execute the query and retrieve the sorted results
    sorted_authors = author_table.all()

    return render_template('authors.html', results=sorted_authors)

@app.route('/delete_author', methods=['POST'])
def delete_author():
    author_id = request.form.get('author_id')
    print(f"Author ID: {author_id}")
    books.remove_author(author_id, verbose=True)

    # Redirect to after deletion
    return redirect('/authors')

if __name__ == '__main__':

    #drop_table('users')

    with app.app_context():
        db.create_all()
        #create_user('admin', 'supersafe') #TODO: existing user exception handling (caused by unique constraint)

    Base.metadata.create_all(bind=engine)
    app.run(debug=True)