import sqlite3 # only used in validate_isbn --> remove?
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased
from sqlalchemy import text

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models import *
import pickle, random, time

def get_title(isbn): # Not sure if this should be in util or in other module
        return Session().query(Books.title).filter_by(isbn13=isbn).scalar()
    # TODO: Code block with similar functions currently in customer.py

def unpickle_dummy(file):
    with open(file, "rb") as f:
        return pickle.load(f)

# Validate ISBN
# Source https://rosettacode.org/wiki/ISBN13_check_digit

# Validate the check digit of an ISBN-13 code:

#  Multiply every other digit by  3.
#  Add these numbers and the other digits.
#  Take the remainder of this number after division by  10.
#  If it is  0,   the ISBN-13 check digit is correct.

def validate_isbn(n: str):
    n = n.replace('-','').replace(' ', '')
    if len(n) != 13:
        return False
    product = (sum(int(ch) for ch in n[::2]) 
               + sum(int(ch) * 3 for ch in n[1::2]))
    return product % 10 == 0

def titles_by_author():
    session = Session()

    try:
        view_query = text('''
        CREATE VIEW TitlarPerFörfattare AS
        SELECT
            CONCAT_WS(' ', a.first_name, a.middle_name, a.last_name) AS Namn,
            DATEDIFF(YEAR, a.birthdate, GETDATE()) AS Ålder,
            COUNT(DISTINCT CASE WHEN ba.author_id IS NOT NULL THEN b.title END) AS Titlar,
            SUM(b.price * i.stock) AS Lagervärde
        FROM
            AUTHORS AS a
        JOIN
            BOOK_AUTHOR_ASSOCIATION AS ba ON a.id = ba.author_id
        JOIN
            BOOKS AS b ON ba.book_isbn13 = b.isbn13
        JOIN
            INVENTORY AS i ON b.isbn13 = i.isbn13
        GROUP BY
            a.first_name, a.middle_name, a.last_name, a.birthdate;
        ''')

        # Execute the view query
        session.execute(view_query)

        print("[!] View created successfully.")
    except Exception as e:
        print(f"Error creating view: {e}")

    session.commit()
    session.close()

def total_sales() -> str:
    with Session() as session:
        total_sales = (
            session
            .query(func.sum(OrderDetail.total_cost))
            .scalar()
        )
        
        sales = round(total_sales or 0)
        
        if sales < 10:
            i = "Oh.."
        elif sales == 69 or sales == 420:
            i = "Nice." 
        elif sales > 10:
            i = "Ok!"
        elif sales > 100:
            i = "Sweet!"
        elif sales > 1000:
            i = "Ay caramba!"
        elif sales > 10_000:
            i = "Wohooo!"
        elif sales > 1_000_000:
            i = "Mr. Bezos.. We meet again."

        return f'Total sales: {sales} coins. {i}'

def welcome_message(username='user'):
    current_hour = int(time.strftime('%H'))

    phrase_1 = ['hej', 'tja', 'tjena', 'hallåj', 'tjabba', 'yo']

    if current_hour < 5 or current_hour >= 19:
        phrase_1 = ['god kväll']
    
    elif 5 <= current_hour <= 9:
        phrase_1 = ['god morgon']

    else:
        phrase_1 = ['hej', 'tja', 'tjena', 'hallåj', 'tjabba', 'yo']

    greeting = random.choice(phrase_1)
    return greeting.capitalize() + ' ' + username + "!"

def remove_null_rows(table_name, column_names, verbose=False):
    with Session() as session:
        try:
            table = globals()[table_name]
            filter_conditions = [getattr(table, column_name) == None for column_name in column_names]
            rows_to_delete = session.query(table).filter(*filter_conditions).all()

            for row in rows_to_delete:
                session.delete(row)
            
            session.commit()

            if verbose:
                print(f'{len(rows_to_delete)} rows removed from {table_name} where {column_names} are null.')
        except SQLAlchemyError as e:
            session.rollback()
            raise e

if __name__ == '__main__':
    pass
    #remove_null_rows('Customer', ['name', 'surname', 'address', 'city', 'state', 'zipcode', 'email'])