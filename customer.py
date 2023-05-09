# For customers
from models import * 


# Hello and wälcome to the bookstöre amazun pls purchase a böwk

def purchase_book(isbn, store_id, customer_id, quantity):
    with Session() as session:

        # Query the inventory for the store and book
        inventory = session.query(Inventory).filter_by(isbn13=isbn, StoreID=store_id).one()

        if inventory.stock < quantity:
            print("Sry, out of stock in this store. Try another store.") #TODO check other stores for customer or smt
            return

        # Update the stock in the inventory & get price
        inventory.stock -= quantity
        
        book_price = session.query(Books.price).filter_by(isbn13=isbn).scalar()

        total_cost = round(book_price * quantity, 2)

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
    book_name = session.query(Books.title).filter_by(isbn13=isbn).scalar()
    store_name = session.query(Store.store_name).filter_by(id=store_id).scalar()
    customer_name = session.query(Customer.name).filter_by(ID=customer_id).scalar()

    # Total books owned and total spending
    total_books_owned = session.query(func.sum(CustomerBooks.copies_owned)).filter_by(customer_id=customer_id).scalar()
    total_spending = session.query(func.sum(Transaction.total_cost)).filter_by(CustomerID=customer_id).scalar()

    unique_books_count = session.query(func.count(distinct(CustomerBooks.book_id))).filter_by(customer_id=customer_id).scalar()

    print(f"{customer_name} purchased {quantity} copies of '{book_name}' (ISBN: {isbn}) from '{store_name}' for a total cost of {total_cost}.")
    print(f"{customer_name} now owns {total_books_owned} book(s) ({unique_books_count} unique) and has a total spending of {total_spending}.")

    remaining_stock = session.query(Inventory.stock).filter_by(isbn13=isbn, StoreID=store_id).scalar()

    if remaining_stock < 10:
        print(f"Heads up! There are only {remaining_stock} copies of '{book_name}' (ISBN: {isbn}) left in stock at '{store_name}'. Order new?")

def get_dummy_cst():

    # Dummy data for Customer table
    customer_data = [
        ('John', 'Doe', 'johndoe@example.com', '123 Main St', 'New York', 'NY', '10001'),
        ('Jane', 'Smith', 'janesmith@example.com', '456 Elm St', 'Los Angeles', 'CA', '90001'),
        ('Bob', 'Johnson', 'bobjohnson@example.com', '789 Oak St', 'Chicago', 'IL', '60601'),
        ('Alice', 'Lee', 'alicelee@example.com', '321 Maple St', 'Houston', 'TX', '77001'),
        ('David', 'Brown', 'davidbrown@example.com', '654 Pine St', 'Philadelphia', 'PA', '19101')
    ]

    with Session() as session:
        for name, surname, address, city, state, zipcode, email in customer_data:
            new_customer = Customer(name=name, surname=surname, address=address, city=city, state=state, zipcode=zipcode, email=email)
            session.add(new_customer)
            session.commit()

if __name__ == '__main__':
    pass
    #Base.metadata.create_all(bind=engine) # Currently only used to add table CustomerBooks(Base)
    #purchase_book("9780007117116", 1, 1, 2)