import pickle
from datetime import datetime

# Store tuple as byte stream
# This file can be removed. Kept for now if we want to change anything in the dummy data.

books = [
    ('9780007117116', 'The Lord of the Rings', 'English', 29.99, datetime(1954, 7, 29), 'Fantasy', 1),
    ('9780439554930', 'Harry Potter and the Philosopher\'s Stone', 'English', 9.99, datetime(1997, 6, 26), 'Fantasy', 2),
    ('9780553801477', 'Foundation', 'English', 19.99, datetime(1951, 5, 1), 'Science Fiction', 3),
    ('9780553588488', 'Ender\'s Game', 'English', 14.99, datetime(1985, 1, 1), 'Science Fiction', 4),
    ('9781400031702', 'The Picture of Dorian Gray', 'English', 10.99, datetime(1890, 7, 1), 'Gothic Fiction', 5),
    ('9780141187761', 'Nineteen Eighty-Four', 'English', 12.99, datetime(1949, 6, 8), 'Dystopian Fiction', 6),
    ('9780316346627', 'A Game of Thrones', 'English', 16.99, datetime(1996, 8, 1), 'Fantasy', 7),
    ('9780061124952', 'American Gods', 'English', 15.99, datetime(2001, 6, 19), 'Fantasy', 8),
    ('9780679745587', 'One Hundred Years of Solitude', 'Spanish', 18.99, datetime(1967, 5, 30), 'Magical Realism', 9),
    ('9780553382563', 'The Hitchhiker\'s Guide to the Galaxy', 'English', 12.99, datetime(1979, 10, 12), 'Science Fiction / Comedy', 10)
    ]

authors = ['J.R.R. Tolkien',
    'J.K. Rowling',
    'Isaac Asimov',
    'Orson Scott Card',
    'Oscar Wilde',
    'George Orwell',
    'George R.R. Martin',
    'Neil Gaiman',
    'Gabriel Garcia Marquez',
    'Douglas Adams'
    ]

customer_data = [
        ('John', 'Doe', 'johndoe@example.com', '123 Main St', 'New York', 'NY', '10001'),
        ('Jane', 'Smith', 'janesmith@example.com', '456 Elm St', 'Los Angeles', 'CA', '90001'),
        ('Bob', 'Johnson', 'bobjohnson@example.com', '789 Oak St', 'Chicago', 'IL', '60601'),
        ('Alice', 'Lee', 'alicelee@example.com', '321 Maple St', 'Houston', 'TX', '77001'),
        ('David', 'Brown', 'davidbrown@example.com', '654 Pine St', 'Philadelphia', 'PA', '19101')
    ]

dummy_tuple = (books, authors, customer_data)
with open ('dummy_tuple', 'wb') as f:
    pickle.dump(starter_content, f)