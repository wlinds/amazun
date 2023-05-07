from models import * 
# models.py currently contain engine, session, declarative_base and Base classes for Author, Book, Store & Inventory

from Scripts.utils import validate_isbn

from sqlalchemy.orm.exc import NoResultFound 
# NoResultFound is currently used only in burn_book() to check if ISBN exist in db

def search_books(search_term):
    session = Session()
    books = (
        session.query(Book, Inventory, Store)
        .join(Inventory.book)
        .join(Inventory.store)
        .filter(Book.Title.ilike(f'%{search_term}%'))
        .all()
    )
    results = {}
    for book, inventory, store in books:
        if book.Title in results:
            results[book.Title].append((store.Store_Name, inventory.Stock))
        else:
            results[book.Title] = [(store.Store_Name, inventory.Stock)]
    return results

def add_book(title, language, price, release_date, author_id, isbn, validate=False, verbose=False):
    isbn = str(isbn) 

    if validate:
        checksum = validate_isbn(isbn)
        if checksum == 0:
            print('ISBN PASS!')
        else:
            raise ValueError('ISBN did not pass validation.')

    session = Session() #TODO Move this to outside function for performance improvements

    # Check if book with specified ISBN already exists
    existing_book = session.query(Book).filter_by(ISBN13=isbn).first()
    if existing_book:
        session.close()
        raise ValueError(f'Book with ISBN {isbn} already exists in the database.')

    new_book = Book(
        ISBN13=isbn,
        Title=title,
        Language=language,
        Price=price,
        Release=release_date,
        AuthID=author_id
    )
    session.add(new_book)
    session.commit()
    session.close()

    if verbose:
        print(f'Added book with ISBN: {isbn} to table.')

def burn_book(isbn, verbose=False):
    session = Session()
    book_to_remove = None

    try:
        book_to_remove = session.query(Book).filter_by(ISBN13=isbn).one()

    except NoResultFound:
        session.close()
        print(f'Book with ISBN {isbn} does not exist in the database.')

    if book_to_remove:
        session.delete(book_to_remove)
        session.commit()
        session.close()
        if verbose:
            print(f'Book with ISBN {isbn} has been removed from the database.')

if __name__ == '__main__':

    # These functions are still a bit wonky TODO
    burn_book("9780123456782", verbose=True)
    add_book('Book7', "English", "12.99", "2023-05-05", 1337, "9780123456782", validate=True, verbose=True)

    results = search_books('Hitchhiker')
    for title, stores in results.items():
        print(f'Title: {title}')
        for store_name, copies_available in stores:
            print(f'    {store_name}: {copies_available} copies available')
