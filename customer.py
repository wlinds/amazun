# For customers
from models import *
from Scripts.utils import unpickle_dummy, remove_null_rows
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError

def purchase_book(isbn, store_id, customer_id, quantity):
    with Session() as session:

        try:
            # Query the inventory for the store and book
            inventory = session.query(Inventory).filter_by(isbn13=isbn, StoreID=store_id).one()

        except NoResultFound:
            print(f"Sry, we're not sure if {isbn=} exists.")
            return

        # TODO: this works IFF the book exists with stock value of 0, otherwise above exception will run
        if inventory.stock < quantity:
            print(f"Sry, {get_title(isbn)} is out of stock in this store.")

            print("Checking other stores...") 

            results = get_stores_by_isbn(isbn)
            store_ids = [result[0] for result in results]
            
            if sum(store_ids) == 0:
                print('Sry, the book could not be found in any store.')
                return

            for store_id in store_ids:
                store_with_book_in_stock = get_store(store_id)
            print(f'Great news, the book {get_title(isbn)} was found at {store_with_book_in_stock}!')
            
            return

        # Update the stock in the inventory & get price
        inventory.stock -= quantity
        total_cost = round(get_book_price(isbn)* quantity, 2)

        # Create a new transaction for the purchase
        transaction = Transaction(isbn13=isbn, StoreID=store_id, CustomerID=customer_id, quantity=quantity, total_cost=total_cost)
        session.add(transaction)

        # Update the customer's list of books
        customer_book = session.query(CustomerBooks).filter_by(customer_id=customer_id, book_id=isbn).first()
        if customer_book:
            customer_book.copies_owned += quantity
        else:
            customer_book = CustomerBooks(customer_id=customer_id, book_id=isbn, copies_owned=quantity)
            session.add(customer_book)

        # Commit the changes to the database
        session.commit()

    # Get the name of the book, store and customer (TODO: probably an easier way to do this)
    book_name, store_name, customer_name = get_title(isbn), get_store(store_id), get_customer(customer_id)

    # Total books owned and total spending
    total_books_owned = session.query(func.sum(CustomerBooks.copies_owned)).filter_by(customer_id=customer_id).scalar()
    total_spending = session.query(func.sum(Transaction.total_cost)).filter_by(CustomerID=customer_id).scalar()

    unique_books_count = session.query(func.count(distinct(CustomerBooks.book_id))).filter_by(customer_id=customer_id).scalar()

    print(f"{customer_name} purchased {quantity} copies of '{book_name}' from {store_name} for a total cost of {total_cost}.")
    print(f"{customer_name} now owns {total_books_owned} book(s) ({unique_books_count} unique) and has a total spending of {total_spending}.")

    remaining_stock = session.query(Inventory.stock).filter_by(isbn13=isbn, StoreID=store_id).scalar()

    if remaining_stock < 10:
        print(f"Heads up! There are only {remaining_stock} copies of '{book_name}' (ISBN: {isbn}) left in stock at '{store_name}'. Order new?")

def get_dummy_cst():
    customer_data = unpickle_dummy(file='starter_content')[3]

    with Session() as session:
        for name, surname, email, address, city, state, zipcode in customer_data:
            existing_customer = session.query(Customer).filter_by(email=email).first()
            if existing_customer:
                continue  # Skip adding the customer if entry already exist
            new_customer = Customer(name=name, surname=surname, address=address, city=city, state=state, zipcode=zipcode, email=email)
            session.add(new_customer)
            session.commit()

            # Create a new entry in the ChangeLog table for customer added
            changelog_entry = ChangeLog(
                table_name='Customer',
                action='added',
                customer_id=new_customer.ID
            )
            session.add(changelog_entry)
            session.commit()

def new_customer(name, surname, address, city, state, zipcode, email, verbose=False):
    with Session() as session:
        new_customer = Customer(name=name, surname=surname, address=address, city=city, state=state, zipcode=zipcode, email=email)
        if verbose:
            print(f'Checking existing customer for email: {email}')
        existing_customer = session.query(Customer).filter_by(email=email).first()
        if existing_customer:
            if verbose:
                print('Email already exist.')
            return None

        session.add(new_customer)
        session.commit()

        # TODO: DRY -- repeated in get_dummy
        changelog_entry = ChangeLog(
            table_name='Customer',
            action='added',
            customer_id=new_customer.ID
        )
        session.add(changelog_entry)
        session.commit()

    if verbose:
        print(f'{name} has successfully been registered as customer.')

        


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
    return Session().query(Books.title).filter_by(isbn13=isbn).one()[0]

def get_store(store_id):
    return Session().query(Store.store_name).filter_by(id=store_id).one()[0]

def get_customer(customer_id):
    return Session().query(Customer.name).filter_by(ID=customer_id).one()[0]

def get_book_price(isbn):
    return Session().query(Books.price).filter_by(isbn13=isbn).scalar()

def get_stores_by_isbn(isbn):
    """Search all stores for isbn in stock."""

    # Define a subquery to filter the Inventory table
    inv_subq = Session().query(Inventory.StoreID).filter_by(isbn13=isbn).subquery()

    # Query the StoreID values from the filtered Inventory table
    store_ids = Session().query(inv_subq.c.StoreID).distinct().all()
    return store_ids

def get_all_customer():
    with Session() as session:
        customers = session.query(Customer).all()
        return customers

# ---------------------------------------------------------------------- #

if __name__ == '__main__':
    purchase_book("9780007117116", 1, 3, 3)
    purchase_book("9780007117116", 2, 3, 3)
    #purchase_book("97806797455817", 1, 3, 3)
    #purchase_book("9780007117116", 1, 3, 3)

    #Base.metadata.create_all(bind=engine) # Currently only used to add table CustomerBooks(Base)
    #purchase_book("9780007117116", 1, 1, 2)