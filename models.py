from sqlalchemy import *
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

# Define database connection

engine = create_engine('sqlite:///amazun.db') # used to communicate with the database and execute SQL statements
Session = sessionmaker(bind=engine)  # used to manage transactions and interact with the ORM layer of SQLAlchemy
Base = declarative_base()  # model class represents a table in the database and its attributes represent columns

#TODO:
# Improve constraints
# Remove declarative_base() (Legacy code)

# Define tables (Old and bulky)

class Author(Base):
    __tablename__ = 'Author'
    ID = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    birthdate = Column(String)
    wiki = Column(String)
    books = relationship('Books', back_populates='author')
    books = relationship('Books', secondary='book_authors', back_populates='authors') # Association table

    # Constraint which only allows unique name + surname combinations
    # IF two authors have identical names, well, tough luck.
    __table_args__ = (
    UniqueConstraint('name', 'surname', name='uq_author_name_surname'),
    )

# Association table
book_authors = Table('book_authors', Base.metadata,
    Column('book_id', Integer, ForeignKey('Books.isbn13')),
    Column('author_id', Integer, ForeignKey('Author.ID')),
)

class Books(Base):
    __tablename__ = 'Books'
    isbn13 = Column(String, primary_key=True)
    title = Column(String)
    language = Column(String)
    price = Column(Integer)
    release = Column(String)
    genre = Column(String, nullable=True)
    AuthID = Column(Integer, ForeignKey('Author.ID'))
    author = relationship('Author', back_populates='books')
    authors = relationship('Author', secondary='book_authors', back_populates='books') # Association table
    inventory = relationship('Inventory', back_populates='book')

class Store(Base):
    __tablename__ = 'Store'
    id = Column(Integer, primary_key=True)
    store_name = Column(String, unique=True)
    store_address = Column(String, unique=True)
    stock = relationship('Inventory', back_populates='store')

    __table_args__ = (
        UniqueConstraint('store_name'),
        UniqueConstraint('store_name', 'store_address'),
    )

class Inventory(Base):
    __tablename__ = 'Inventory'
    StoreID = Column(Integer, ForeignKey('Store.id'), primary_key=True)
    isbn13 = Column(String, ForeignKey('Books.isbn13'), primary_key=True)
    stock = Column(Integer)
    store = relationship('Store', back_populates='stock')
    book = relationship('Books', back_populates='inventory')

class Customer(Base):
    __tablename__ = 'Customer'
    ID = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zipcode = Column(String)
    email = Column(String)

    created_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)


class CustomerBooks(Base):
    __tablename__ = 'Customer_Books'
    customer_id = Column(Integer, ForeignKey('Customer.ID'), primary_key=True)
    book_id = Column(String(13), ForeignKey('Books.isbn13'), primary_key=True)
    copies_owned = Column(Integer, default=0)

class Transaction(Base):
    __tablename__ = 'Transactions'
    id = Column(Integer, primary_key=True)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    CustomerID = Column(Integer, ForeignKey('Customer.ID'))
    #customer = relationship("Customer")
    isbn13 = Column(String(13), ForeignKey('Books.isbn13'))
    StoreID = Column(Integer)
    book = relationship("Books")
    quantity = Column(Integer)
    total_cost = Column(Numeric(precision=2))

class ChangeLog(Base):
    __tablename__ = 'changelog'

    id = Column(Integer, primary_key=True)
    table_name = Column(String)
    action = Column(String)
    customer_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

if __name__ == '__main__':

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    book = Books(isbn13='123456789', title='Example Book', language='English', price=20)
    author1 = Author(name='John', surname='Doe')
    author2 = Author(name='Jane', surname='Smith')

    book.authors.append(author1)
    book.authors.append(author2)

    session.add(book)
    session.commit()

    session.close()
