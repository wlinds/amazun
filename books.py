from models import * # models.py contain engine, session, declarative_base and table Base classes
from Scripts.utils import validate_isbn

from sqlalchemy.orm.exc import NoResultFound  # NoResultFound is currently used only in burn_book() to check if ISBN exist in db
from sqlalchemy.exc import IntegrityError # Used to check duplicates in get_dummy_books
from sqlalchemy.orm import aliased # Used to find authors in multiple tables
import logging

from datetime import datetime

def get_isbn(title):
    session = Session()
    book = session.query(Book).filter_by(title=title).first()
    session.close()

    if book:
        return book.isbn13
    else:
        return None

def find_all_by_author(author_id, verbose=False):
    session = Session()

    try:
        found_books = (
            session.query(Book)
            .join(book_author_association, Book.isbn13 == book_author_association.c.book_isbn13, isouter=True)
            .join(Author, Author.id == book_author_association.c.author_id, isouter=True)
            .filter((Author.id == author_id) | (Author.id == author_id))
            .all()
        )

        author = session.query(Author).filter_by(id=author_id).first()

        if verbose:
            if author:
                print(f"Books by {author.first_name} {author.last_name}:")
                for book in found_books:
                    print(f"- {book.title}")
            else:
                print(f"Author with ID {author_id} not found.")

        return found_books

    except Exception as e:
        print(f"An error occurred while querying: {str(e)}")
        return None

    finally:
        session.close()

def get_author_name(author_id):
    session = Session()
    author = session.query(Author).filter_by(id=author_id).first()
    session.close()

    if author:
        return f'{author.name} {author.surname}'
    else:
        return None

def add_author(first_name, last_name, birthdate, wiki_link=None, verbose=False):
    with Session() as session:
        existing_author = session.query(Author).filter_by(first_name=first_name, last_name=last_name).first()

        if existing_author:
            print(f'{first_name} {last_name} already exists in the database. Skipping...')
            return

        new_auth = Author(
            first_name=first_name,
            last_name=last_name,
            birthdate=birthdate,
            wiki_link=wiki_link
        )
        session.add(new_auth)
        session.commit()

        if verbose:
            last_id = session.query(Author.id).order_by(Author.id.desc()).first()[0]
            print(f'{first_name} {last_name} added with ID {last_id}.\n')

def add_new(title, language, price, release_date, author_name, isbn, genre, validate=False, verbose=False):
    """
    Add a book to Book table.
    """
    # TODO: checksum is broken, look into
    isbn = str(isbn)
    if validate:
        checksum = validate_isbn(isbn)
        if checksum != 0:
            raise ValueError('ISBN did not pass validation.')
        else:
            print('ISBN PASS!')

    session = Session()  # TODO: Move this to outside function for performance improvements

    try:
        # Check if book with specified ISBN already exists
        existing_book = session.query(Book).filter_by(isbn13=isbn).first()
        if existing_book:
            print(f'Book with ISBN {isbn} already exists in the database.')
            return

        # Check if author with specified name exists, or create new author
        author = session.query(Author).filter_by(first_name=author_name).first()
        if not author:
            # If author doesn't exist, split the name into first_name and last_name
            split_name = author_name.split()
            first_name = split_name[0]
            last_name = " ".join(split_name[1:])
            author = Author(first_name=first_name, last_name=last_name)
            session.add(author)

        new_book = Book(
            isbn13=isbn,
            title=title,
            language=language,
            price=price,
            release_date=release_date,
            genre=genre,
        )
        
        new_book.authors.append(author)  # Associate the book with the author
        
        session.add(new_book)
        session.commit()
        if verbose:
            print(f'Successfully registered {title}, {isbn}.')

    except Exception as e:
        session.rollback()
        print(f'An error occurred while adding the book: {str(e)}')

    finally:
        session.close()

def burn_book(isbn, verbose=False):
    """
    Remove book from both Inventory & Book table.
    """
    session = Session()

    try:
        book_to_remove = session.query(Book).filter_by(isbn13=isbn).one()
    except NoResultFound:
        session.close()
        print(f'Book with ISBN {isbn} does not exist in the database.')
        return

    try:
        inventory_to_remove = session.query(Inventory).filter_by(isbn13=isbn).all()
    except NoResultFound:
        inventory_to_remove = None

    if inventory_to_remove:
        title = session.query(Book.title).filter_by(isbn13=isbn).one()[0] # Only for printing title
        for inventory in inventory_to_remove:
            session.delete(inventory)

    session.delete(book_to_remove)
    session.commit()
    session.close()

    if verbose:
        print(f"All copies of {title} have been burned.")

def get_dummy_authors():
    """
    Adds default authors to Author table.
    """

    authors = [
        ('J.R.R. Tolkien', datetime(1892, 1, 3), 'https://en.wikipedia.org/wiki/J._R._R._Tolkien'),
        ('J.K. Rowling', datetime(1965, 7, 31), 'https://en.wikipedia.org/wiki/J._K._Rowling'),
        ('Isaac Asimov', datetime(1920, 1, 2), 'https://en.wikipedia.org/wiki/Isaac_Asimov'),
        ('Orson Scott Card', datetime(1951, 8, 24), 'https://en.wikipedia.org/wiki/Orson_Scott_Card'),
        ('Oscar Wilde', datetime(1854, 10, 16), 'https://en.wikipedia.org/wiki/Oscar_Wilde'),
        ('George Orwell', datetime(1903, 6, 25), 'https://en.wikipedia.org/wiki/George_Orwell'),
        ('George R.R. Martin', datetime(1948, 9, 20), 'https://en.wikipedia.org/wiki/George_R._R._Martin'),
        ('Gabriel Garcia Marquez', datetime(1927, 3, 6), 'https://en.wikipedia.org/wiki/Gabriel_García_Márquez'),
        ('Douglas Adams', datetime(1952, 3, 11), 'https://en.wikipedia.org/wiki/Douglas_Adams'),
        ('Terry Pratchett', datetime(1948, 4, 28), 'https://en.wikipedia.org/wiki/Terry_Pratchett'),
        ('Neil Gaiman', datetime(1960, 11, 10), 'https://en.wikipedia.org/wiki/Neil_Gaiman')
    ]
    
    with Session() as session:
        for author_name, birthdate, wiki_link in authors:
            split_name = author_name.split()
            first_name = split_name[0]
            last_name = " ".join(split_name[1:])

            try:
                new_author = Author(first_name=first_name, last_name=last_name, birthdate=birthdate, wiki_link=wiki_link)
                session.add(new_author)
                session.commit()

            except IntegrityError:
                logging.warning(f"Author '{author_name}' already exists.")
                session.rollback()

def remove_author(author_id, remove_all_null=False, verbose=False):
    # Very similar to remove_customer() in books.py. TODO: merge into one function

    with Session() as session:
        try:
            author = session.query(Author).filter_by(ID=author_id).first()
            if author:
                session.delete(author)
                session.commit()
                if remove_all_null:
                    remove_null_rows('Author', ['name', 'surname', 'birthdate', 'wiki'], verbose=verbose)

                if verbose:
                    print(f'{author_id=} deleted.')

            else:
                if verbose:
                    print(f'{author_id=} does not exist.')
                    
        except SQLAlchemyError as e:
            session.rollback()
            raise e

def add_books_to_authors(books_info):
    with Session() as session:
        for book_info in books_info:
            title, language, price, release_date, authors, isbn13, genre = book_info

            # Check if the book already exists by ISBN-13
            existing_book = session.query(Book).filter_by(isbn13=isbn13).first()

            if existing_book:
                logging.warning(f"Book '{title}' with ISBN-13 '{isbn13}' already exists. Skipping.")
            else:
                new_book = Book(
                    isbn13=isbn13,
                    title=title,
                    language=language,
                    price=price,
                    release_date=release_date,
                    genre=genre
                )
                session.add(new_book)
                session.commit()

                author_objects = []
                for author_name in authors:
                    first_name, last_name = author_name.split(' ', 1)
                    author = session.query(Author).filter_by(first_name=first_name, last_name=last_name).first()
                    if author:
                        author_objects.append(author)
                    else:
                        new_author = Author(first_name=first_name, last_name=last_name)
                        session.add(new_author)
                        session.commit()
                        author_objects.append(new_author)
                
                new_book.authors = author_objects
                session.commit()

                logging.info(f"Book '{title}' added to authors: {[author_name for author_name in authors]}")

if __name__ == '__main__':
    pass
    #main_db = 'amazun.db'

    #Base.metadata.create_all(bind=engine)

    #print(get_author_name(2))

    #get_dummy_books()
    
    #add_new(title='Pyton for dummies', language='English', price='9.99', release_date=datetime(2015, 10, 29), author_id='none', isbn=9781473214714, genre='Educational', verbose=True)


    # These functions are still a bit wonky TODO
    
    #burn_book("978012345", verbose=True)
    #add_book('Book7', "English", "12.99", "2023-05-05", 1337, "978012345", validate=True, verbose=True)

    #add_to_inventory("9780553801477", 1, 99)

    #results = search_books('Hitchhiker')
    #for title, stores in results.items():
    #    print(f'Title: {title}')
    #    for store_name, copies_available in stores:
    #        print(f'    {store_name}: {copies_available} copies available')
