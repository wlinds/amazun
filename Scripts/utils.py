import sqlite3 # only used in validate_isbn --> remove?
from sqlalchemy.exc import SQLAlchemyError

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



# Vy: ”TitlarPerFörfattare”
def titles_by_author():

    session = Session()

    try:

        view_query = text('''
            CREATE VIEW TitlarPerFörfattare AS
            SELECT
                Author.Name + ' ' + Author.surname AS Namn,
                DATEDIFF(year, Author.birthdate, GETDATE()) AS Ålder,
                COUNT(DISTINCT CASE WHEN Books.AuthID IS NOT NULL THEN Books.title END) AS Titlar,
                SUM(Books.price * Inventory.stock) AS Lagervärde
            FROM
                Author
                JOIN Books ON Author.ID = Books.AuthID
                JOIN Inventory ON Books.isbn13 = Inventory.isbn13
            GROUP BY
                Author.Name, Author.surname, Author.birthdate
        ''')

        # Execute the view query
        session.execute(view_query)

        print("View created successfully.")
    except Exception as e:
        print(f"Error creating view: {e}")

    session.commit()
    session.close()

# Drop table OR view
# https://www.sqlitetutorial.net/sqlite-create-view/

def drop_table(name, file_name='amazun.db'):
    conn = sqlite3.connect(file_name)
    c = conn.cursor()

    try:
        c.execute(f"DROP TABLE {name}")
    except sqlite3.OperationalError:
        try:
            c.execute(f"DROP VIEW {name}")
        except sqlite3.OperationalError:
            print(f"No table or view named {name} found in database.")

    conn.commit()
    conn.close()

def total_sales():
    with Session() as session:
        total_sales = session.query(func.sum(Transaction.total_cost)).scalar()
        sales = round(total_sales)
        if sales < 10:
            i = "Oh.."
        elif sales == 69 or sales == 420:
            i = "Nice." 
        elif sales > 100:
            i = "Ok!"
        elif sales > 1000:
            i = "Sweet!"
        elif sales > 10_000:
            i = "Ay caramba!"
        elif sales > 100_000:
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
    update_changelog(add)
    #remove_null_rows('Customer', ['name', 'surname', 'address', 'city', 'state', 'zipcode', 'email'])