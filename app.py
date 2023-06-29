from models import *
from Scripts import author_crawler
import os, secrets, store_manager, books, customer
from Scripts.utils import titles_by_author, get_title, total_sales, welcome_message, drop_table
from flask import Flask, render_template, request, redirect, session, current_app, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

#database_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'amazun.db'))
#app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'

cstring2 = "mssql+pyodbc://SA:superSafe123@localhost:1433/amazun?driver=ODBC+Driver+17+for+SQL+Server"
app.config['SQLALCHEMY_DATABASE_URI'] = cstring2
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
db = SQLAlchemy(app)

# Access the user session
def check_login():
    return session.get('user_id'), session.get('username')

# Define the User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(256))

    def set_password(self, password):
        if isinstance(password, bytes):
            password = password.decode('utf-8')
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

def create_user(username, password):
    with app.app_context():
        try:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            print(f"User with username '{username}' already exists.")

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user is not None and user.check_password(password):
            flash('Successful authentication') #TODO: this is SOMETIMES displayed when entering incorrect info?
            session['user_id'] = user.id
            session['username'] = user.username
            
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

# @app.route('/base') # Can probably be removed?
# def base():
#     return render_template('base.html')

@app.route('/dashboard')
def dashboard():
    user_id, username = check_login()

    if user_id:
        welcome = welcome_message(username)
        return render_template('dashboard.html', greeting=welcome)
    else:
        # User is not authenticated, redirect
        return redirect(url_for('login'))

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    user_id, username = check_login()
    
    if request.method == 'POST' and user_id:
        selected_isbn = request.form.get('isbn')
        selected_store_id = request.form.get('store_id')
        selected_quantity = request.form.get('quantity')

        # Call add_to_inventory()
        store_manager.add_to_inventory(selected_isbn, selected_store_id, int(selected_quantity), verbose=True)

    if user_id:
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
    else:
        # User is not authenticated, redirect
        return redirect(url_for('login'))


@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    user_id, username = check_login()

    if request.method == 'POST' and user_id:
        selected_isbn = request.form.get('isbn')
        selected_store_id = request.form.get('store_id')
        selected_customer_id = request.form.get('customer_id')
        selected_quantity = request.form.get('quantity')

        # Call purchase_book()
        customer.purchase_book(selected_isbn, selected_store_id, selected_customer_id, int(selected_quantity))

    if user_id:
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
    else:
    # User is not authenticated, redirect
        return redirect(url_for('login'))


@app.route('/customers', methods=['GET', 'POST'])
def customers():
    user_id, username = check_login()

    if request.method == 'POST' and user_id:
        name = request.form.get('name')
        surname = request.form.get('surname')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        zipcode = request.form.get('zipcode')
        email = request.form.get('email')

        customer.new_customer(name, surname, address, city, state, zipcode, email, verbose=True)

    if user_id:
        customer_table = db.session.query(Customer).all()

        return render_template('customers.html',
                               results=customer_table)

    else:
    # User is not authenticated, redirect
        return redirect(url_for('login'))

@app.route('/delete_customer', methods=['POST'])
def delete_customer():
    user_id, username = check_login()

    if user_id:
        customer_id = request.form.get('customer_id')
        print(f"Customer ID: {customer_id}")
        customer.remove_customer(customer_id, verbose=True)

        # Redirect to after deletion
        return redirect('/customers')
    
    else:
    # User is not authenticated, redirect
        return redirect(url_for('login'))

@app.route('/authors', methods=['GET', 'POST'])
def authors():
    user_id, username = check_login()

    if user_id:
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
    
    else:
    # User is not authenticated, redirect
        return redirect(url_for('login'))

@app.route('/delete_author', methods=['POST'])
def delete_author():
    user_id, username = check_login()

    if user_id:
        author_id = request.form.get('author_id')
        print(f"Author ID: {author_id}")
        books.remove_author(author_id, verbose=True)

        # Redirect to after deletion
        return redirect('/authors')
    else:
    # User is not authenticated, redirect
        return redirect(url_for('login'))

@app.route('/search_book', methods=['GET', 'POST'])
def search():
    user_id, username = check_login()

    if user_id:
        results = None
        if request.method == 'POST':
            search_term = request.form.get('search_term')
            results = store_manager.search_books(search_term)
        return render_template('search_book.html', results=results)
    else:
    # User is not authenticated, redirect
        return redirect(url_for('login'))

@app.route('/author_scraper', methods=['GET', 'POST'])
def author_scraper():
    user_id, username = check_login()

    if user_id:
        return render_template('author_scraper.html')
    else:
        # User is not authenticated, redirect
        return redirect(url_for('login'))

@app.route('/start_crawler', methods=['POST'])
def start_crawler():
    user_id, username = check_login()

    if user_id:
        output_messages = author_crawler.crawl_wikipedia_authors()
        return render_template('author_scraper.html', output_messages=output_messages)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)

    with app.app_context():
        db.create_all()
        create_user('admin2', 'supersafe') #TODO: existing user exception handling (caused by unique constraint)

    Base.metadata.create_all(bind=engine)
    app.run(debug=True)
    