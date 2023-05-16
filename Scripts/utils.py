import sqlite3
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
        # Create the view query
        # This got incredibly long because I had to
        # count books where an author is listed in the Books table directly,
        # and also in the book_authors association table.

        view_query = text('''
            CREATE VIEW TitlarPerFörfattare AS
            SELECT
                Author.Name || ' ' || Author.surname AS Namn,
                strftime('%Y', 'now') - strftime('%Y', Author.birthdate) AS Ålder,
                COALESCE(t1.Titlar, 0) + COALESCE(t2.Titlar, 0) AS Titlar,
                SUM(Books.price * Inventory.stock) AS Lagervärde
            FROM
                Author
                JOIN Books ON Author.ID = Books.AuthID
                JOIN Inventory ON Books.isbn13 = Inventory.isbn13
                LEFT JOIN (
                    SELECT
                        Books.AuthID AS AuthorID,
                        COUNT(DISTINCT Books.title) AS Titlar
                    FROM
                        Books
                    GROUP BY
                        Books.AuthID
                ) AS t1 ON Author.ID = t1.AuthorID
                LEFT JOIN (
                    SELECT
                        book_authors.author_id AS AuthorID,
                        COUNT(DISTINCT Books.title) AS Titlar
                    FROM
                        book_authors
                        JOIN Books ON book_authors.book_id = Books.isbn13
                    GROUP BY
                        book_authors.author_id
                ) AS t2 ON Author.ID = t2.AuthorID
            GROUP BY
                Author.name, Author.surname
            ORDER BY
                Namn
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
    
    elif current_hour > 5 or current_hour <= 9:
        phrase_1 = ['god morgon']   

    greeting = random.choice(phrase_1)
    return greeting.capitalize() + ' ' + username + "!"