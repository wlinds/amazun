import os
import sqlite3
from get_dummy_cst import *
from get_dummy_store import *
from utils import titles_by_author

def create_basic_tables(file_name='amazun'):
    # Script to create initial database

    conn = sqlite3.connect(f'{file_name}.db')
    c = conn.cursor()

    # Table 1: Author
    c.execute('''CREATE TABLE Author (
                    ID INTEGER PRIMARY KEY,
                    Name TEXT NOT NULL,
                    Surname TEXT NOT NULL,
                    Birthdate DATE NOT NULL)''')


    # Table 2: Book (ISBN13 as the primary key and AuthID as a foreign key to Author.ID)
    # TBH I don't think 'Price' should be in this table as it is subject to change, but fk it we ball for now
    c.execute('''CREATE TABLE Book (
                    ISBN13 TEXT PRIMARY KEY,
                    Title TEXT NOT NULL,
                    Language TEXT NOT NULL,
                    Price REAL NOT NULL,
                    Release DATE NOT NULL,
                    AuthID INTEGER NOT NULL,
                    FOREIGN KEY (AuthID) REFERENCES Author(ID))''')

    # Table 3: Store
    c.execute('''CREATE TABLE Store (
                    ID INTEGER PRIMARY KEY,
                    Store_Name TEXT NOT NULL,
                    Store_Address TEXT NOT NULL)''')

    # Table 4: Inventory (StoreID and ISBN13 as composite PK)
    c.execute('''CREATE TABLE Inventory (
                    StoreID INTEGER NOT NULL,
                    ISBN13 TEXT NOT NULL,
                    Stock INTEGER NOT NULL,
                    PRIMARY KEY (StoreID, ISBN13),
                    FOREIGN KEY (StoreID) REFERENCES Store(ID),
                    FOREIGN KEY (ISBN13) REFERENCES Book(ISBN13))''')

    conn.commit()
    conn.close()

def extend_db(file_name='amazun'):
    # Script to extend db with Customer and Orders tables

    conn = sqlite3.connect(f'{file_name}.db')
    c = conn.cursor()

   # Table 5: Customer
    c.execute('''CREATE TABLE Cst (
                    ID INTEGER PRIMARY KEY,
                    Name TEXT NOT NULL,
                    Surname TEXT NOT NULL,
                    Address TEXT NOT NULL,
                    City TEXT NOT NULL,
                    State TEXT NOT NULL,
                    ZipCode TEXT NOT NULL,
                    Email TEXT NOT NULL)''')

    # Table 6: Customer Order
    c.execute('''CREATE TABLE Cst_Order (
                    OrderID INTEGER PRIMARY KEY,
                    CustomerID INTEGER NOT NULL,
                    Order_Date DATE NOT NULL,
                    Expected_Delivery DATE NOT NULL,
                    Total_Price REAL NOT NULL,
                    FOREIGN KEY (CustomerID) REFERENCES Cst(ID))''')

    # Table 7: Customer Order Item
    c.execute('''CREATE TABLE Cst_Order_Items (
                    OrderID INTEGER NOT NULL,
                    ISBN13 TEXT NOT NULL,
                    Units INTEGER NOT NULL,
                    Shipped_From TEXT NOT NULL,
                    PRIMARY KEY (OrderID, ISBN13),
                    FOREIGN KEY (OrderID) REFERENCES Cst_Order(OrderID),
                    FOREIGN KEY (ISBN13) REFERENCES Book(ISBN13))''')

    # By using this table, we can link the Cst_Order table to the Cst_Order_Item table via the OrderID foreign key.
    # This will allow us to retrieve all the items that have been bought for a particular order, and also all the orders in which a particular item has been bought.
    # This /should/ work as intended, but maybe its not the best way. TODO

    conn.commit()
    conn.close()

if __name__ == "__main__":

    main_db = 'amazun.db'

    if os.path.exists(main_db):
        os.remove(main_db)
        print(f'{main_db} removed')
    else:
        print("File does not exist")

    create_basic_tables()
    extend_db()
    get_dummy_store()
    populate_customer_table()
    get_dummy_orders()
    titles_by_author()
