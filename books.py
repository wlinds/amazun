from models import * # models.py contain engine, session, declarative_base and table Base classes
from Scripts.utils import validate_isbn, unpickle_dummy

from sqlalchemy.orm.exc import NoResultFound  # NoResultFound is currently used only in burn_book() to check if ISBN exist in db
from sqlalchemy.exc import IntegrityError # Used to check duplicates in get_dummy_books

def search_books(search_term):
    """
    Search for books currently in store
    """

    session = Session()
    filter_book = (
        session.query(Books, Inventory, Store)
        .join(Inventory.book)
        .join(Inventory.store)
        .filter(Books.title.ilike(f'%{search_term}%'))
        .all()
    )
    results = {}
    for book, inventory, store in filter_book:
        if book.title in results:
            results[book.title].append((store.store_name, inventory.stock))
        else:
            results[book.title] = [(store.store_name, inventory.stock)]
    return results

def add_book(title, language, price, release_date, author_id, isbn, validate=False, verbose=False):
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
        AuthID=author_id
    )
    session.add(new_book)
    session.commit()
    session.close()

    if verbose:
        print(f'Added book with ISBN: {isbn} to table.')

def add_all_books(store_id=1, copies=400, verbose=False):
    with Session() as session:
        all_books = session.query(Books).all()
        for book in all_books:
            isbn = book.isbn13
            add_to_inventory(isbn, store_id, copies)
        session.commit()
    if verbose:
        store_name = session.query(Store.store_name).filter_by(id=store_id).scalar()
        print(f'Added {copies} of all existing books to {store_name}')

# TODO: This add_all_books() create a session and then calls add_to_inventory() which also 
# creates a session. I'm surprised this works with no errors, but it might be stupid/slow.


def add_to_inventory(isbn, store_id, copies, verbose=False):
    """
    Add book to Inventory table.
    """

    session = Session()
    inventory = session.query(Inventory).filter_by(isbn13=isbn, StoreID=store_id).first()
    if inventory:
        inventory.stock += copies
    else:
        inventory = Inventory(isbn13=isbn, StoreID=store_id, stock=copies)
        session.add(inventory)
    session.commit()

    if verbose:
        store_name = session.query(Store.store_name).filter_by(id=store_id).scalar()
        print(f'Added {copies} copies of {isbn} to {store_name}.')

def burn_book(isbn, verbose=False):
    """
    Remove book from both Inventory & Book table.
    """
    session = Session()

    try:
        book_to_remove = session.query(Book).filter_by(ISBN13=isbn).one()
    except NoResultFound:
        session.close()
        print(f'Book with ISBN {isbn} does not exist in the database.')
        return

    try:
        inventory_to_remove = session.query(Inventory).filter_by(ISBN13=isbn).all()
    except NoResultFound:
        inventory_to_remove = None

    if inventory_to_remove:
        for inventory in inventory_to_remove:
            session.delete(inventory)

    session.delete(book_to_remove)
    session.commit()
    session.close()

    if verbose:
        print(f'Book with ISBN {isbn} and its associated inventory have been removed from the database.')

def get_dummy_books():
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
