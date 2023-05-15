from models import *
import os, books, customer
import store_manager as store
from Scripts.utils import titles_by_author, get_title, total_sales

if __name__ == '__main__':
    main_db = 'amazun.db'

    if os.path.exists(main_db):
        os.remove(main_db)
        print(f'{main_db} removed')

    Base.metadata.create_all(bind=engine)

    store.get_dummy_stores()
    books.get_dummy_books()
    books.get_dummy_authors()


    # Add 200 copies of Lord of The Rings to Store 1
    store.add_to_inventory(9780007117116, 1, 200, verbose=True)

    # Add 5000 copies of ALL existing books to store 2:
    store.add_all_books(store_id=2, copies=5000, verbose=True)

    # Add view #TODO: Missing date of birth
    titles_by_author()

    # Add dummy customers
    customer.get_dummy_cst()

    # Search book
    search_title = "The"
    results = store.search_books(search_title)
    print(f'Searching for books containing "{search_title}"')

    for i in results:
        print(i)

    # Customer book purchase
    customer.purchase_book(9780007117116, 1, 1, 10)
    customer.purchase_book(9780007117116, 2, 2, 1)

    # Move books
    store.move_books(9780007117116, 2, 3, 1000)
    store.move_books(9780007117116, 1, 2, 190)
    customer.purchase_book("9780007117116", 1, 3, 3)
    customer.purchase_book("9780007117116", 3, 3, 3)

    print(total_sales())

    # Add customer
    customer.new_customer('Sixth Amorite King Hammurobi', 'King of the Old Babylonian Empire', 'Mušḫuššu', 'Babylon', 'Mesopotamia', 'none', 'amorite_king@anumail.com', verbose=True)
    customer.new_customer('Anna', 'Esperanto', 'Hjortronvägen 12', 'Göteborg', 'Västa Götaland', '431 42', 'anna@example.com', verbose=True)

    # Add author
    books.add_author('God', 'Christ', datetime(1, 1, 1), verbose=True)

    # Add book to existence (add to book table)
    books.add_new('Pyton for dummies', 'English', '9.99', datetime(2015, 10, 29), 'null', 9781473214714, 'Educational', verbose=True)
    store.add_to_inventory(9781473214714, 2, 200, verbose=True)

    books.add_new('The Old Testament (Original)', 'English', '9.99', datetime(2015, 10, 29), '1', 9780195378405, 'Artefact', verbose=True)
    store.add_to_inventory(9780195378405, 2, 1, verbose=True)

    # Add new store
    store.add_store('Catholic Church', 'Vatican City', verbose=False)
    store.move_books(9780195378405, 2, 4, 1)

    # Remove book
    books.burn_book(9780195378405, verbose=True)

    # Count customer
    all_customer = customer.get_all_customer()
    print(f'Customers: {len(all_customer)}')
    for customer in all_customer:
        print(f'{customer.name} {customer.surname}')


    # Multiple authors, (association table in models.py) TODO: Make this a function
    session = Session()
    book = session.query(Books).filter_by(isbn13='9781473214712').first()
    author1 = session.query(Author).filter_by(name='Terry', surname='Pratchett').first()
    author2 = session.query(Author).filter_by(name='Neil', surname='Gaiman').first()

    book.authors.append(author1)
    book.authors.append(author2)

    session.add(book)
    session.commit()

    # Add book to store inventory by searching title
    store.add_to_inventory(books.get_isbn('Good Omens'), 2, 10, verbose=True)
    # Maybe the add_to_inventory should be modified to take either isbn or title as args instead.

    # Find all books by author
    books.find_all_by_author(8, verbose=True)
    books.find_all_by_author(11, verbose=True)
    books.find_all_by_author(1, verbose=True)