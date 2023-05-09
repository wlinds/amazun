from models import *
from sqlalchemy.exc import IntegrityError

def add_store(name: str, address: str):
    """
    Create a new store.
    """

    with Session() as session:
        try:
            new_store = Store(store_name=name, store_address=address)
            session.add(new_store)
            session.commit()
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

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine) # Used to create and enforce constraints on Store
    add_store("Baloo2", "Sturegatan 13")
    get_dummy_stores()