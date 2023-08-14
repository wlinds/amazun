from sqlalchemy import *
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.orm import clear_mappers # debugging
from my_credentials import cstring2
from datetime import datetime

# Define database connection
# This has to be created first using Azure Data Studio or similar, maybe possible to do with sqlalchemy straight away, idk.
engine = create_engine(cstring2)
Session = sessionmaker(bind=engine)

Base = declarative_base()

# Use this for SQLite:
#engine = create_engine('sqlite:///amazun.db') # used to communicate with the database and execute SQL statements
#Session = sessionmaker(bind=engine)  # used to manage transactions and interact with the ORM layer of SQLAlchemy
#Base = declarative_base()  # model class represents a table in the database and its attributes represent columns

class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    first_name = Column(NVARCHAR(255), nullable=False)
    middle_name = Column(NVARCHAR(255))
    last_name = Column(NVARCHAR(255), nullable=False)
    birthdate = Column(DATETIME2(timezone=True))
    wiki_link = Column(NVARCHAR(255))
    books = relationship('Book', secondary='book_author_association', back_populates='authors')

    # Add a unique constraint on first_name, middle_name, and last_name
    __table_args__ = (
        UniqueConstraint('first_name', 'middle_name', 'last_name', name='_uq_author_name'),
    )


# Association table, many-to-many relationship
book_author_association = Table('book_author_association', Base.metadata,
    Column('book_isbn13', String(13), ForeignKey('books.isbn13')),
    Column('author_id', Integer, ForeignKey('authors.id')),
)

class Store(Base):
    __tablename__ = 'stores'
    id = Column(Integer, primary_key=True)
    store_name = Column(NVARCHAR(255), unique=True)
    store_address = Column(NVARCHAR(255), unique=True)
    stock = relationship('Inventory', back_populates='store')

    __table_args__ = (
        UniqueConstraint('store_name', 'store_address'),
    )

class Inventory(Base):
    __tablename__ = 'inventory'
    store_id = Column(Integer, ForeignKey('stores.id'), primary_key=True)
    isbn13 = Column(String(13), ForeignKey('books.isbn13'), primary_key=True)
    stock = Column(Integer)
    store = relationship('Store', back_populates='stock')
    book = relationship('Book', back_populates='inventory')

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    first_name = Column(NVARCHAR(255))
    last_name = Column(NVARCHAR(255))
    address = Column(NVARCHAR(255))
    city = Column(NVARCHAR(255))
    state = Column(NVARCHAR(255))
    zipcode = Column(NVARCHAR(255))
    email = Column(NVARCHAR(255))
    created_at = Column(DATETIME2(timezone=True), default=func.now())
    deleted_at = Column(DATETIME2(timezone=True), nullable=True)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_date = Column(DATETIME2(timezone=True), default=func.now())
    customer_id = Column(Integer, ForeignKey('customers.id'))
    customer = relationship("Customer")
    store_id = Column(Integer, ForeignKey('stores.id'))
    store = relationship("Store")

class OrderDetail(Base):
    __tablename__ = 'order_details'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    book_isbn13 = Column(String(13), ForeignKey('books.isbn13'))
    book = relationship("Book")
    quantity = Column(Integer)
    total_cost = Column(Float)

class ChangeLog(Base):
    __tablename__ = 'changelog'
    id = Column(Integer, primary_key=True)
    table_name = Column(NVARCHAR(255))
    action = Column(NVARCHAR(255))
    customer_id = Column(Integer)
    timestamp = Column(DATETIME2(timezone=True), default=func.now())

class Book(Base):
    __tablename__ = 'books'
    isbn13 = Column(String(13), primary_key=True)
    title = Column(NVARCHAR(255))
    language = Column(NVARCHAR(255))
    price = Column(Float)
    release_date = Column(DATETIME2(timezone=True))
    genre = Column(NVARCHAR(255), nullable=True)
    authors = relationship('Author', secondary='book_author_association', back_populates='books')
    inventory = relationship('Inventory', back_populates='book')
    
if __name__ == '__main__':
    clear_mappers()

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)