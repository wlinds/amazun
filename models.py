from sqlalchemy import *
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Define database connection
engine = create_engine('sqlite:///amazun.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Author(Base):
    __tablename__ = 'Author'
    ID = Column(Integer, primary_key=True)
    Name = Column(String)
    Surname = Column(String)
    Birthdate = Column(String)
    books = relationship('Book', back_populates='author')

class Book(Base):
    __tablename__ = 'Book'
    ISBN13 = Column(String, primary_key=True)
    Title = Column(String)
    Language = Column(String)
    Price = Column(Integer)
    Release = Column(String)
    AuthID = Column(Integer, ForeignKey('Author.ID'))
    author = relationship('Author', back_populates='books')
    stock = relationship('Inventory', back_populates='book')

class Store(Base):
    __tablename__ = 'Store'
    ID = Column(Integer, primary_key=True)
    Store_Name = Column(String)
    Store_Address = Column(String)
    stock = relationship('Inventory', back_populates='store')

class Inventory(Base):
    __tablename__ = 'Inventory'
    StoreID = Column(Integer, ForeignKey('Store.ID'), primary_key=True)
    ISBN13 = Column(String, ForeignKey('Book.ISBN13'), primary_key=True)
    Stock = Column(Integer)
    store = relationship('Store', back_populates='stock')
    book = relationship('Book', back_populates='stock')