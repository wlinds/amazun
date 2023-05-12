from models import *
import os, store_manager, books, customer
from Scripts.utils import titles_by_author, get_title, total_sales
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
database_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'amazun.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
db = SQLAlchemy(app)

@app.route('/transactions')
def view():
    transaction_table = db.session.query(Transaction).all()

    sales_info = total_sales()

    return render_template('transactions.html', results=transaction_table, total_sales=sales_info)

#TODO: Route for drop down purchases

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    app.run(debug=True)