# amazun bookstore

![Alt text](Assets/Img/fancy_logo.png)

SQL Project. No unionizing pls.




## Tables
Table 1: Author
‘ID’ (Primary Key), ‘Name’, ‘Surname’, ‘Birthdate’

Table 2: Book
‘ISBN13’ (Primary Key), ‘Title’, ‘Language’, ‘Price’, ‘Release’, ‘AuthID’.

Table 3: Store
‘ID’ (Primary Key), ‘Store_Name’, ‘Store_Address’

Table 4: Inventory
‘StoreID’, ‘ISBN13’, ‘Stock’
Composite Key: ‘StoreID’ & ‘ISBN13’

Table 5: Cst (Customer)
‘ID’ (Primary Key), ‘Name’, ‘Surname’, ‘Address’, ‘City’, ‘State’, ‘ZipCode’, ‘Email’

Table 6: Cst_Order (Customer order)
‘OrderID’ (Primary Key), ‘CustomerID’, ‘Order_Date’, ‘Expected_Delivery’, ‘Total_Price’

Table 7: Cst_Order_Items (Customer Order Items)
‘OrderID (Primary Key)’, ‘ISBN13’ (Primary key), ‘Units’, ‘Shipped_From’