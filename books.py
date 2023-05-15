from models import * # models.py contain engine, session, declarative_base and table Base classes
from Scripts.utils import validate_isbn, unpickle_dummy

from sqlalchemy.orm.exc import NoResultFound  # NoResultFound is currently used only in burn_book() to check if ISBN exist in db
from sqlalchemy.exc import IntegrityError # Used to check duplicates in get_dummy_books
import logging

def add_author(name, surname, birthdate, verbose=False):
    with Session() as session:
        new_auth = Author(
            name=name,
            surname=surname,
            birthdate=birthdate
        )
        session.add(new_auth)
        session.commit()

    if verbose:
            last_id = session.query(Author.ID).order_by(Author.ID.desc()).first()[0]
            print(f'{name} has probably been added and received AuthID {last_id}.')

def add_new(title, language, price, release_date, author_id, isbn, genre, validate=False, verbose=False):
    """
    Add a book to Book table.
    """
    
    #TODO: checksum is broken, look into
    isbn = str(isbn) 
    if validate:
        checksum = validate_isbn(isbn)
        if checksum != 0:
            raise ValueError('ISBN did not pass validation.')
        else:
            print('ISBN PASS!')

    session = Session() #TODO Move this to outside function for performance improvements

    # Check if book with specified ISBN already exists
    existing_book = session.query(Books).filter_by(isbn13=isbn).first()
    if existing_book:
        session.close()
        raise ValueError(f'Book with ISBN {isbn} already exists in the database.')

    new_book = Books(
        isbn13=isbn,
        title=title,
        language=language,
        price=price,
        release=release_date,
        genre=genre,
        AuthID=author_id
    )
    session.add(new_book)
    session.commit()
    session.close()

    if verbose:
        print(f'Successfully registered {title}, {isbn} as book.')

def burn_book(isbn, verbose=False):
    """
    Remove book from both Inventory & Book table.
    """
    session = Session()

    try:
        book_to_remove = session.query(Books).filter_by(isbn13=isbn).one()
    except NoResultFound:
        session.close()
        print(f'Book with ISBN {isbn} does not exist in the database.')
        return

    try:
        inventory_to_remove = session.query(Inventory).filter_by(isbn13=isbn).all()
    except NoResultFound:
        inventory_to_remove = None

    if inventory_to_remove:
        title = session.query(Books.title).filter_by(isbn13=isbn).one()[0] # Only for printing title
        for inventory in inventory_to_remove:
            session.delete(inventory)

    session.delete(book_to_remove)
    session.commit()
    session.close()

    if verbose:
        print(f"All copies of {title} have been burned.")

def get_dummy_books():
    """
    Adds 11 default books to Books table.
    """
    books = unpickle_dummy()[0]

    with Session() as session:
        for isbn, title, language, price, release, genre, author in books:
            try:
                new_book = Books(isbn13=isbn, title=title, language=language, price=price, release=release, genre=genre, AuthID=author)
                session.add(new_book)
                session.commit()

            except IntegrityError:
                print(f"Book '{isbn}' already exists as {title}.")
                session.rollback()

def get_dummy_authors():
    """
    Adds 12 default authors to Author table.
    """
    authors = unpickle_dummy()[1]
    with Session() as session:
        for author_name in authors:
            split_name = author_name.split()
            first_name = split_name[0]
            last_name = " ".join(split_name[1:])

            try:
                new_author = Author(name=first_name, surname=last_name)
                session.add(new_author)
                session.commit()

            except IntegrityError:
                logging.warning(f"Author '{author_name}' already exists.")
                session.rollback()


if __name__ == '__main__':
    main_db = 'amazun.db'

    Base.metadata.create_all(bind=engine) 


    # These functions are still a bit wonky TODO
    
    #burn_book("978012345", verbose=True)
    #add_book('Book7', "English", "12.99", "2023-05-05", 1337, "978012345", validate=True, verbose=True)

    #add_to_inventory("9780553801477", 1, 99)

    #results = search_books('Hitchhiker')
    #for title, stores in results.items():
    #    print(f'Title: {title}')
    #    for store_name, copies_available in stores:
    #        print(f'    {store_name}: {copies_available} copies available')
