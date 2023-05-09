from models import *
import os, store_manager, books, customer
from Scripts.utils import titles_by_author

if __name__ == '__main__':
    main_db = 'amazun.db'

    #if os.path.exists(main_db):
    #    os.remove(main_db)
    #    print(f'{main_db} removed')
#
    Base.metadata.create_all(bind=engine)

    store_manager.get_dummy_stores()
    books.get_dummy_books()
    books.get_dummy_authors()

    # Add 200 copies of Lord of The Rings to Store 1
    books.add_to_inventory(9780007117116, 1, 200, verbose=True)

    # Add 4000 copies of ALL existing books to store 1:
    books.add_all_books(store_id=1, copies=5000, verbose=True)

    # Add view
    titles_by_author()

    # Add dummy customers
    customer.get_dummy_cst()

    print('Complete')

    #TODO: cst purchases books (name variables updated to snake_case in models), check Customer_Books 