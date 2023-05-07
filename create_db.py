import sqlite3

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

if __name__ == "__main__":
    create_basic_tables()