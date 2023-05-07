import sqlite3
from random import randint
from datetime import datetime, timedelta

conn = sqlite3.connect('amazun.db')
c = conn.cursor()

authors = [
    ('John', 'Doe', datetime(1970, 1, 1)),
    ('Jane', 'Doe', datetime(1980, 1, 1)),
    ('Bob', 'Smith', datetime(1990, 1, 1)),
    ('Alice', 'Jones', datetime(2000, 1, 1))
]

books = [
    ('9780007117116', 'The Lord of the Rings', 'English', 29.99, datetime(1954, 7, 29), 1),
    ('9780439554930', 'Harry Potter and the Philosopher\'s Stone', 'English', 9.99, datetime(1997, 6, 26), 2),
    ('9780553801477', 'Foundation', 'English', 19.99, datetime(1951, 5, 1), 3),
    ('9780553588488', 'Ender\'s Game', 'English', 14.99, datetime(1985, 1, 1), 4)
]

stores = [
    ('123 Main St.', 'New York'),
    ('456 Elm St.', 'Los Angeles'),
    ('789 Oak St.', 'Chicago'),
    ('321 Pine St.', 'Houston')
]

# Define some functions to generate random data
def generate_random_date(start_date, end_date):
    time_between = end_date - start_date
    days_between = time_between.days
    random_number_of_days = randint(0, days_between)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date

def generate_random_stock():
    return randint(0, 100)

# Insert example data into the Author table
for author in authors:
    c.execute("INSERT INTO Author (Name, Surname, Birthdate) VALUES (?, ?, ?)", author)

# Insert example data into the Book table
for book in books:
    c.execute("INSERT INTO Book (ISBN13, Title, Language, Price, Release, AuthID) VALUES (?, ?, ?, ?, ?, ?)", book)

# Insert example data into the Store table
for store in stores:
    c.execute("INSERT INTO Store (Store_Name, Store_Address) VALUES (?, ?)", store)

# Insert example data into the Inventory table
for store_id in range(1, len(stores)+1):
    for isbn in range(1, len(books)+1):
        stock = generate_random_stock()
        c.execute("INSERT INTO Inventory (StoreID, ISBN13, Stock) VALUES (?, ?, ?)", (store_id, books[isbn-1][0], stock))

# Save changes and close connection to the database
conn.commit()
conn.close()
