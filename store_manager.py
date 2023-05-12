from models import *
from sqlalchemy.exc import IntegrityError

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

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine) # Used to create and enforce constraints on Store
    add_store("Baloo2", "Sturegatan 13")
    get_dummy_stores()