# For customers
from models import *
from Scripts.utils import unpickle_dummy, remove_null_rows
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from sqlalchemy.orm import joinedload


def purchase_books(customer_id, purchase_info):
    session = Session()

    try:
        # Check if the customer exists
        customer = session.query(Customer).get(customer_id)
        if not customer:
            raise ValueError("Customer not found.")

        for isbn, store_id, quantity in purchase_info:
            # Query the inventory for the book and store
            inventory = (
                session.query(Inventory)
                .options(joinedload(Inventory.store))
                .filter_by(isbn13=isbn, store_id=store_id)
                .first()
            )

            if not inventory or inventory.stock < quantity:
                print(f"Error: '{get_title(isbn)}' is not available in sufficient quantity.")
                continue

            book_price = inventory.book.price
            total_cost = round(book_price * quantity, 2)

            # Create an order
            order = Order(customer_id=customer_id, store_id=store_id)
            session.add(order)
            session.flush()  # Get the order ID

            # Create an order detail
            order_detail = OrderDetail(
                order_id=order.id,
                book_isbn13=isbn,
                quantity=quantity,
                total_cost=total_cost
            )
            session.add(order_detail)

            # Update inventory
            inventory.stock -= quantity

        # Commit the transaction
        session.commit()

        print("Purchase successful.")
    except ValueError as ve:
        print(f"Error: {ve}")
        session.rollback()
    except Exception as e:
        print(f"Error: An unexpected error occurred. {e}")
        session.rollback()
    finally:
        session.close()

def get_dummy_cst():
    print('get_dummt cst running')
    customer_data = unpickle_dummy(file='starter_content')[3]

    with Session() as session:
        for first, last, email, address, city, state, zipcode in customer_data:
            existing_customer = session.query(Customer).filter_by(email=email).first()
            if existing_customer:
                continue  # Skip adding the customer if entry already exist
            new_customer = Customer(first_name=first, last_name=last, address=address, city=city, state=state, zipcode=zipcode, email=email)
            session.add(new_customer)
            session.commit()

            # Create a new entry in the ChangeLog table for customer added
            changelog_entry = ChangeLog(
                table_name='Customer',
                action='added',
                customer_id=new_customer.id
            )
            session.add(changelog_entry)
            session.commit()

def new_customer(first_name, last_name, address, city, state, zipcode, email, verbose=False):
    with Session() as session:
        new_customer = Customer(first_name=first_name, last_name=last_name, address=address, city=city, state=state, zipcode=zipcode, email=email)
        if verbose:
            print(f'Checking existing customer for email: {email}')
        existing_customer = session.query(Customer).filter_by(email=email).first()
        if existing_customer:
            if verbose:
                print('Email already registered.')
            return None

        session.add(new_customer)
        session.commit()

        # TODO: DRY -- repeated in get_dummy
        changelog_entry = ChangeLog(
            table_name='Customer',
            action='added',
            customer_id=new_customer.id
        )
        session.add(changelog_entry)
        session.commit()

    if verbose:
        print(f'{first_name} {last_name} has successfully been registered as customer.')

        


def remove_customer(customer_id, remove_all_null=False, verbose=False):
    with Session() as session:
        try:
            customer = session.query(Customer).filter_by(ID=customer_id).first()
            if customer:
                session.delete(customer)
                session.commit()
                if remove_all_null:
                    remove_null_rows('Customer', ['name', 'surname', 'address', 'city', 'state', 'zipcode', 'email'], verbose=verbose)

                if verbose:
                    print(f'{customer_id=} deleted.')

                # Create a new entry in the ChangeLog table for customer deleted
                changelog_entry = ChangeLog(
                    table_name='Customer',
                    action='deleted',
                    customer_id=customer_id
                )
                session.add(changelog_entry)
                session.commit()

            else:
                if verbose:
                    print(f'{customer_id=} does not exist.')
        except SQLAlchemyError as e:
            session.rollback()
            raise e

# -- TODO: Where to put this? Utils? Also: make it just one function? -- #
def get_title(isbn):
    session = Session()
    try:
        book = session.query(Book).filter_by(isbn13=isbn).first()
        return book.title if book else None
    finally:
        session.close()

def get_store(store_id):
    session = Session()
    try:
        store = session.query(Store).get(store_id)
        return store.store_name if store else None
    finally:
        session.close()

def get_customer(customer_id):
    session = Session()
    try:
        customer = session.query(Customer).filter_by(id=customer_id).first()
        return f"{customer.first_name} {customer.last_name}" if customer else None
    finally:
        session.close()

def get_book_price(isbn):
    session = Session()
    try:
        book = session.query(Book).filter_by(isbn13=isbn).first()
        return book.price if book else None
    finally:
        session.close()

def get_stores_by_isbn(isbn):
    session = Session()
    try:
        inv_subq = session.query(Inventory.store_id).filter_by(isbn13=isbn).subquery()
        store_ids = session.query(inv_subq.c.store_id).distinct().all()
        return store_ids
    finally:
        session.close()

def get_all_customer():
    session = Session()
    try:
        customers = session.query(Customer).all()
        return customers
    finally:
        session.close()

# ---------------------------------------------------------------------- #

if __name__ == '__main__':
    purchase_book("9780007117116", 1, 3, 3)
    purchase_book("9780007117116", 2, 3, 3)
    #purchase_book("97806797455817", 1, 3, 3)
    #purchase_book("9780007117116", 1, 3, 3)

    #Base.metadata.create_all(bind=engine) # Currently only used to add table CustomerBooks(Base)
    #purchase_book("9780007117116", 1, 1, 2)