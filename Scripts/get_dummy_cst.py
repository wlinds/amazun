import sqlite3

def populate_customer_table():
    conn = sqlite3.connect('amazun.db')
    c = conn.cursor()

    # Dummy data for Customer table
    customer_data = [
        ('John', 'Doe', 'johndoe@example.com', '123 Main St', 'New York', 'NY', '10001'),
        ('Jane', 'Smith', 'janesmith@example.com', '456 Elm St', 'Los Angeles', 'CA', '90001'),
        ('Bob', 'Johnson', 'bobjohnson@example.com', '789 Oak St', 'Chicago', 'IL', '60601'),
        ('Alice', 'Lee', 'alicelee@example.com', '321 Maple St', 'Houston', 'TX', '77001'),
        ('David', 'Brown', 'davidbrown@example.com', '654 Pine St', 'Philadelphia', 'PA', '19101')
    ]

    for customer in customer_data:
        c.execute("INSERT INTO Cst (Name, Surname, Email, Address, City, State, ZipCode) VALUES (?, ?, ?, ?, ?, ?, ?)", customer)

    conn.commit()
    conn.close()


def get_dummy_orders():
    conn = sqlite3.connect('amazun.db')
    c = conn.cursor()

    # Dummy data for Cst_Order table
    order_data = [
        (1, '2023-05-01', '2023-05-05', 100.00),
        (2, '2023-05-02', '2023-05-06', 50.00),
        (3, '2023-05-03', '2023-05-07', 75.00),
        (4, '2023-05-04', '2023-05-08', 200.00),
        (5, '2023-05-05', '2023-05-09', 150.00)
    ]

    #TODO CustomerID rename in table?

    for order in order_data:
        c.execute("INSERT INTO Cst_Order (CustomerID, Order_Date, Expected_Delivery, Total_Price) VALUES (?, ?, ?, ?)", order)

    
    # Dummy data for Cst_Order_Items table TODO

    order_item_data = [
        (1, 'ISBN-001', 2, 'New York'),
        (1, 'ISBN-002', 1, 'New York'),
        (2, 'ISBN-003', 3, 'Los Angeles'),
        (2, 'ISBN-004', 1, 'Los Angeles'),
        (3, 'ISBN-001', 1, 'Chicago'),
        (3, 'ISBN-004', 2, 'Chicago'),
        (4, 'ISBN-002', 5, 'Philadelphia'),
        (5, 'ISBN-003', 4, 'Houston'),
        (5, 'ISBN-005', 1, 'Houston')
    ]

    for order_item in order_item_data:
        c.execute("INSERT INTO Cst_Order_Items (OrderID, ISBN13, Units, Shipped_from) VALUES (?, ?, ?, ?)", order_item)

    conn.commit()
    conn.close()
