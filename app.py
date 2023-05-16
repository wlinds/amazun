from models import *
import os, store_manager, books, customer
from Scripts.utils import titles_by_author, get_title, total_sales, welcome_message
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
database_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'amazun.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def home():

    welcome = welcome_message(username='Shiva')

    return render_template('index.html', message=welcome)


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

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    app.run(debug=True)