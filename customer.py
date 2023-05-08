# For customers
from models import * 

# Hello and wälcome to the bookstöre amazun pls purchase a böwk

def purchase_book(isbn, store_id, customer_id, quantity):
    with Session() as session:

        # Query the inventory for the store and book
        inventory = session.query(Inventory).filter_by(ISBN13=isbn, StoreID=store_id).one()

        if inventory.Stock < quantity:
            print("Sry, out of stock in this store. Try another store.") #TODO check other stores for customer or smt
            return

        # Update the stock in the inventory & get price
        inventory.Stock -= quantity
        
        book_price = session.query(Book.Price).filter_by(ISBN13=isbn).scalar()

        total_cost = round(book_price * quantity, 2)

        # Create a new transaction for the purchase
        transaction = Transaction(ISBN13=isbn, StoreID=store_id, CustomerID=customer_id, Quantity=quantity, Total_Cost=total_cost)
        session.add(transaction)

        # Commit the changes to the database
        session.commit()

        # Get the name of the book, store and customer (TODO: probably an easier way to do this)
        book_name = session.query(Book.Title).filter_by(ISBN13=isbn).scalar()
        store_name = session.query(Store.Store_Name).filter_by(ID=store_id).scalar()
        customer_name = session.query(Customer.Name).filter_by(ID=customer_id).scalar()

        print(f"{customer_name} purchased {quantity} copies of '{book_name}' (ISBN: {isbn}) from '{store_name}' for a total cost of {total_cost}.")

        remaining_stock = session.query(Inventory.Stock).filter_by(ISBN13=isbn, StoreID=store_id).scalar()

        print(f"There are {remaining_stock} copies of '{book_name}' (ISBN: {isbn}) left in stock at '{store_name}'.")


if __name__ == '__main__':
    purchase_book("9780007117116", 1, 1, 2)
