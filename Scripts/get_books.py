import requests
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dateutil.parser import parse as parse_date
import datetime

def is_valid_isbn(isbn): # very lazy check but it'll do
    if len(isbn) == 13:
        return True
    return False

def is_valid_date(date_str): # also lazy
    try:
        datetime.datetime.strptime(date_str, "%y-%m-%d")
        return True
    except ValueError:
        return False

def get_books(author):
    """Finds books by the given author using the Google Books API."""
    print(f'get_books called with {author}')
    url = "https://www.googleapis.com/books/v1/volumes?q=inauthor:{}".format(author)
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.content)
        books = []
        
        for item in data.get("items", []):
            volume_info = item.get("volumeInfo", {})
            
            title = volume_info.get("title")
            authors = volume_info.get("authors", [])

            #TODO some books only have year and month, not day, this will cause a crash
            publication_date = None
            
            # Update publication_date if available in the API response
            if "publishedDate" in volume_info:
                publication_date = volume_info["publishedDate"]
            
            isbn_identifier = volume_info.get("industryIdentifiers", [])
            isbn = isbn_identifier[0]["identifier"] if isbn_identifier and is_valid_isbn(isbn_identifier[0]["identifier"]) else "N/A"
            genre = volume_info.get("genres", [])

            if is_valid_date != None:
                if is_valid_date(publication_date) == False:
                    publication_date = None

            book = {
                "title": title,
                "author": authors[0] if authors else "N/A",
                "publication_date": publication_date,
                "isbn": isbn,
                "genre": genre
            }
            books.append(book)
            
        return books
    else:
        print(f"Error: API request failed with status code {response.status_code}.")

if __name__ == "__main__":
    pass
