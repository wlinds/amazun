from models import *
from sqlalchemy.exc import IntegrityError

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

def add_store(name: str, address: str, verbose=False):
    """
    Create a new store.
    """

    with Session() as session:
        try:
            new_store = Store(store_name=name, store_address=address)
            session.add(new_store)
            session.commit()
            if verbose:
                print(f"Added store '{name}'")
        except IntegrityError:
            print(f"Store '{name}' already exists")

def get_dummy_stores():
    dummy_stores = [
        ('Toads Books', 'Mushroom Kingdom'),
        ('The Great Library', 'Alexandria'),
        ('Böcker & Babbel', 'Shinar'),
    ]
    with Session() as session:
        for name, address in dummy_stores:
            try:
                new_store = Store(store_name=name, store_address=address)
                session.add(new_store)
                session.commit()
            except IntegrityError:
                print(f"Store '{name}' already exists")
                session.rollback()

def move_books(isbn, from_store_id, to_store_id, quantity):
    with Session() as session:
        try:
            # Check if there is enough stock at the source store
            source_inventory = session.query(Inventory).filter_by(isbn13=isbn, StoreID=from_store_id).first()
            if not source_inventory or source_inventory.stock < quantity:
                print(f'Not enough ISBN {isbn} in stock at store {from_store_id} to fulfill transfer.')
                return False

            # Subtract stock from source store
            source_inventory.stock -= quantity

            # Add stock to destination store
            destination_inventory = session.query(Inventory).filter_by(isbn13=isbn, StoreID=to_store_id).first()
            if not destination_inventory:
                destination_inventory = Inventory(isbn13=isbn, StoreID=to_store_id, stock=0)
                session.add(destination_inventory)
            destination_inventory.stock += quantity

            session.commit()

            # Get store name
            from_store_title = session.query(Store.store_name).filter_by(id=from_store_id).one()[0]
            to_store_title = session.query(Store.store_name).filter_by(id=to_store_id).one()[0]

            print(f"{quantity} copies of ISBN {isbn} moved from {from_store_title} to {to_store_title}.")
            return True

        except IntegrityError as e:
            print(f"Error: {e}. Rollback.")
            session.rollback()
            return False

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
        title = session.query(Books.title).filter_by(isbn13=isbn).one()[0]
        store_name = session.query(Store.store_name).filter_by(id=store_id).one()[0]
        print(f'Added {copies} copies of {title}, {isbn} to {store_name}.')


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine) # Used to create and enforce constraints on Store
    add_store("Baloo2", "Sturegatan 13")
    get_dummy_stores()