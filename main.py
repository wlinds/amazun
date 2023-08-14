from models import *
import os
import books as book_operations
import customer as customer_ops
import store_manager as store_ops
from Scripts.utils import get_title, total_sales, titles_by_author
from Scripts.author_crawler import crawl_wikipedia_authors

from datetime import datetime

if __name__ == '__main__':
    # main_db = 'amazun.db'  # Used for SQLite

    # Base.metadata.create_all(bind=engine)

    store_ops.get_dummy_stores()
    book_operations.get_dummy_authors()

    # List of tuples containing book information
    books_info = [
    ('The Fellowship of the Ring', 'English', 12.99, datetime(1954, 7, 29), ['J.R.R. Tolkien'], '9780007117116', 'Fantasy'),
    ('Harry Potter and the Sorcerer\'s Stone', 'English', 9.99, datetime(1997, 6, 26), ['J.K. Rowling'], '9780439554930', 'Fantasy'),
    ('Foundation', 'English', 19.99, datetime(1951, 5, 1), ['Isaac Asimov'], '9780553801477', 'Science Fiction'),
    ('Good Omens', 'English', '15.99', datetime(2015, 10, 29), ['Neil Gaiman', 'Terry Pratchett'], '9781473214712', 'Horror / Fantasy / Comedy')
    ]

    # Call the function to add books to authors
    book_operations.add_books_to_authors(books_info)

    # Add 200 copies of Lord of The Rings to Store 1
    store_ops.add_to_inventory(9780007117116, 1, 200, verbose=True)

    # Add 5000 copies of ALL existing books to store 2:
    store_ops.add_all_books(store_id=2, copies=5000, verbose=True)

    # Add view # TODO

    # Search book test
    search_title = "The"
    results = store_ops.search_books(search_title)
    print(f'Searching for books containing "{search_title}"')

    for data in results.values():
        book_info = data['book_info']

        print("Book Details:")
        print(f"Title: {book_info['title']}")
        print(f"ISBN: {book_info['isbn']}")
        print(f"Language: {book_info['language']}")
        print(f"Price: {book_info['price']}")
        print(f"Release Date: {book_info['release_date']}")
        print(f"Genre: {book_info['genre']}")
        print(f"Author: {book_info['author']}")

        print("Available Stores and Inventory:")
        for store_name, stock in data['stores']:
            print(f"Store: {store_name}, Stock: {stock}")

        print("=" * 30)

    # Add dummy customers
    customer_ops.get_dummy_cst()

    # Purchase books test
    customer_id = 1
    purchase_info = [
        ("9780007117116", 1, 2),  # ISBN, Store ID, Quantity
        ("9780553801477", 2, 1),
    ]
    customer_ops.purchase_books(customer_id, purchase_info)

    # Move books
    store_ops.move_books(9780007117116, 2, 3, 1000)
    store_ops.move_books(9780007117116, 1, 2, 190)

    print(total_sales())

    # Add customers
    customer_ops.new_customer('Sixth Amorite King Hammurobi', 'King of the Old Babylonian Empire', 'Mušḫuššu', 'Babylon', 'Mesopotamia', 'none', 'amorite_king@anumail.com', verbose=True)
    customer_ops.new_customer('Anna', 'Esperanto', 'Hjortronvägen 12', 'Göteborg', 'Västra Götaland', '431 42', 'anna@example.com', verbose=True)
    customer_ops.new_customer('Per', 'Bolund', 'Torpdalen 12', 'Stockholm', 'Stockholms län', '111 22', 'perra@gmail.com', verbose=True)

    # Testing dupes
    customer_ops.new_customer('Sixth Amorite King Hammurobi', 'King of the Old Babylonian Empire', 'Mušḫuššu', 'Babylon', 'Mesopotamia', 'none', 'amorite_king@anumail.com', verbose=True)

    # Add author
    book_operations.add_author('God', 'Christ', datetime(1, 1, 1), wiki_link='https://en.wikipedia.org/wiki/God_in_Christianity', verbose=True)
    book_operations.add_author('God', 'Christ', datetime(1, 1, 1), wiki_link='https://en.wikipedia.org/wiki/God_in_Christianity', verbose=True)
    book_operations.add_author('asdf', 'asdfgg', datetime(1, 1, 1), wiki_link='https://en.wikipedia.org/wiki/God_in_Christianity', verbose=True)

    # Add book to existence (add to book table)
    book_operations.add_new('Python for Dummies', 'English', '9.99', datetime(2015, 10, 29), '25', '9781473214714', 'Educational', verbose=True)

    # Add book to store inventory
    store_ops.add_to_inventory('9781473214714', 2, 200, verbose=True)

    book_operations.add_new('The Old Testament (Original)', 'English', '9.99', datetime(2015, 10, 29), '1', 9780195378405, 'Artifact', verbose=True)
    store_ops.add_to_inventory(9780195378405, 2, 1, verbose=True)

    # Add new store
    store_ops.add_store('Catholic Church', 'Vatican City', verbose=False)
    store_ops.move_books(9780195378405, 2, 4, 1)

    # Remove book
    book_operations.burn_book(9780195378405, verbose=True)

    # Count customers
    all_customers = customer_ops.get_all_customer()
    print(f'Customers: {len(all_customers)}')
    for cust in all_customers:
        print(f'{cust.first_name} {cust.last_name}')

    # Add book to store inventory by searching title
    store_ops.add_to_inventory(book_operations.get_isbn('Good Omens'), 2, 10, verbose=True)
    # Maybe the add_to_inventory should be modified to take either isbn or title as args instead.

    # Create view
    titles_by_author()

    # ---------------------------------------------------------------------------------------------- #

    # Find all books by author
    book_operations.find_all_by_author(8, verbose=True)
    book_operations.find_all_by_author(11, verbose=True)
    book_operations.find_all_by_author(10, verbose=True)
    book_operations.find_all_by_author(1, verbose=True)

    authors = crawl_wikipedia_authors(max_authors=20)

    with Session() as session:
        for author_info in authors:
            split_name = author_info[0].split()
            first_name = split_name[0]
            last_name = " ".join(split_name[1:])
            birthdate = author_info[1]
            print(first_name, last_name, birthdate)
            new_author = Author(
                first_name=first_name,
                last_name=last_name,
                birthdate=birthdate
            )
            session.add(new_author)
        session.commit()