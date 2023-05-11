import sqlite3
from models import *
import pickle

def get_title(isbn): # Not sure if this should be in util or in other module
        return Session().query(Books.title).filter_by(isbn13=isbn).scalar()
    # TODO: Code block with similar functions currently in customer.py

def unpickle_dummy():
    with open("starter_content", "rb") as f:
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
    conn = sqlite3.connect('amazun.db')
    c = conn.cursor()

    try:
    # Create the view
        c.execute('''CREATE VIEW TitlarPerFörfattare AS
                        SELECT Author.Name || ' ' || Author.surname AS Namn,
                               strftime('%Y', 'now') - strftime('%Y', Author.birthdate) AS Ålder,
                               COUNT(DISTINCT Books.title) AS Titlar,
                               SUM(Books.price * Inventory.stock) AS Lagervärde
                        FROM Author
                        JOIN Books ON Author.ID = Books.AuthID
                        JOIN Inventory ON Books.isbn13 = Inventory.isbn13
                        GROUP BY Author.name, Author.surname
                        ORDER BY Namn''')
        print("View created successfully.")
    except sqlite3.OperationalError:
        print("View already exists.")
        
    conn.commit()
    conn.close()


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

        print(f'Total sales: {sales} coins. {i}')