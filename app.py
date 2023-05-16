from models import *
import os, store_manager, books, customer
from Scripts.utils import titles_by_author, get_title, total_sales, welcome_message
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
database_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'amazun.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
db = SQLAlchemy(app)

@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/', methods=['GET', 'POST'])
def home():

    welcome = welcome_message(username='Shiva')
    return render_template('index.html', message=welcome)

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

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    app.run(debug=True)