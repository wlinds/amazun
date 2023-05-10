import sqlite3
from models import *

def get_title(isbn):
        return Session().query(Books.title).filter_by(isbn13=isbn).scalar()


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

