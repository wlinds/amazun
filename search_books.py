from models import *
# models.py currently contain engine, session, declarative_base and Base classes for Author, Book, Store & Inventory

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

if __name__ == '__main__':

    results = search_books('Hitchhiker')
    for title, stores in results.items():
        print(f'Title: {title}')
        for store_name, copies_available in stores:
            print(f'    {store_name}: {copies_available} copies available')
