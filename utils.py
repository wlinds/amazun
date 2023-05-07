import sqlite3

# Validate ISBN
# Source https://rosettacode.org/wiki/ISBN13_check_digit

# Validate the check digit of an ISBN-13 code:

#  Multiply every other digit by  3.
#  Add these numbers and the other digits.
#  Take the remainder of this number after division by  10.
#  If it is  0,   the ISBN-13 check digit is correct.

def validate_isbn(n):
    n = n.replace('-','').replace(' ', '')
    if len(n) != 13:
        return False
    product = (sum(int(ch) for ch in n[::2]) 
               + sum(int(ch) * 3 for ch in n[1::2]))
    return product % 10 == 0




# Vy: ”TitlarPerFörfattare”
def titles_by_author():
    conn = sqlite3.connect('amazun.db')
    c = conn.cursor()

    # Create the view
    c.execute('''CREATE VIEW TitlarPerFörfattare AS
                    SELECT Author.Name || ' ' || Author.Surname AS Namn,
                           strftime('%Y', 'now') - strftime('%Y', Author.Birthdate) AS Ålder,
                           COUNT(DISTINCT Book.Title) AS Titlar,
                           SUM(Book.Price * Inventory.Stock) AS Lagervärde
                    FROM Author
                    JOIN Book ON Author.ID = Book.AuthID
                    JOIN Inventory ON Book.ISBN13 = Inventory.ISBN13
                    GROUP BY Author.Name, Author.Surname
                    ORDER BY Namn''')

    conn.commit()
    conn.close()

titles_by_author()
