from models import *
import os, store_manager, books, customer
from Scripts.utils import titles_by_author, get_title, total_sales

if __name__ == '__main__':
    main_db = 'amazun.db'

    if os.path.exists(main_db):
        os.remove(main_db)
        print(f'{main_db} removed')

    Base.metadata.create_all(bind=engine)

    store_manager.get_dummy_stores()
    books.get_dummy_books()
    books.get_dummy_authors()


    # Add 200 copies of Lord of The Rings to Store 1
    books.add_to_inventory(9780007117116, 1, 200, verbose=True)

    # Add 5000 copies of ALL existing books to store 2:
    books.add_all_books(store_id=2, copies=5000, verbose=True)

    # Add view #TODO: Missing date of birth
    titles_by_author()

    # Add dummy customers
    customer.get_dummy_cst()

    # Search book
    results = books.search_books("The")
    for i in results:
        print(i)

    # Customer book purchase
    customer.purchase_book(9780007117116, 1, 1, 10)
    customer.purchase_book(9780007117116, 2, 2, 1)
    # Move books
    store_manager.move_books(9780007117116, 2, 3, 1000)
    store_manager.move_books(9780007117116, 1, 2, 190)
    customer.purchase_book("9780007117116", 1, 3, 3)
    customer.purchase_book("9780007117116", 3, 3, 3)

    total_sales()

