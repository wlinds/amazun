import requests, random
from bs4 import BeautifulSoup
import time # not used, perhaps should set delay somewhere...

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from books import add_author

# Find authors and date of birth on Wikipedia by
# random crawl through Writers subcategories

# TODO: Check max_author, as it seem to go on past given limit.

def crawl_wikipedia_authors(category_url='https://en.wikipedia.org/wiki/Category:Writers', subcategory_hierarchy=[], max_authors=100):
    return crawl_category(category_url, subcategory_hierarchy, max_authors=max_authors)

def crawl_category(category_url, subcategory_hierarchy=[], max_authors=100):
    base_url = 'https://en.wikipedia.org'
    authors = []
    author_count = 0

    # Send a request to the category page
    response = requests.get(category_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find subcategories within the category page
    subcategories = soup.find('div', {'id': 'mw-subcategories'})
    if subcategories:
        links = subcategories.find_all('a')
        subcategory_urls = [base_url + link['href'] for link in links]
        random.shuffle(subcategory_urls)  # Shuffle the subcategory URLs

        # Iterate over subcategories and find author pages
        for subcategory_url in subcategory_urls:
            subcategory_name = subcategory_url.split('/')[-1]
            subcategory_hierarchy.append(subcategory_name)
            print(f"Subcategory Hierarchy: {' > '.join(subcategory_hierarchy)}")
            crawl_category(subcategory_url, subcategory_hierarchy, max_authors=max_authors)
            subcategory_hierarchy.pop()

            if author_count >= max_authors:
                break

    # Find author pages within the category page
    pages = soup.find('div', {'id': 'mw-pages'})
    if pages:
        links = pages.find_all('a')
        author_urls = [link['href'] for link in links]

        # Process each author page
        for author_url in author_urls:
            author_info = process_author_page(author_url)
            if author_info:
                authors.append(author_info)
                author_count += 1

                if author_count >= max_authors:
                    break

    return authors

def process_author_page(author_url):
    author_page_url = 'https://en.wikipedia.org' + author_url

    # Send a request to the author page
    response = requests.get(author_page_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Filter for excluding movies (if infobox contains release)
    stop_keywords = ['release', 'movie', 'film', 'Joakim Lamotte', 'statue', 'play', 'opera', 'memorial']  # List of stop keywords
    infobox = soup.find('table', {'class': 'infobox'})
    if infobox:
        found_keywords = [keyword for keyword in stop_keywords if keyword in infobox.text.lower()]
        if found_keywords:
            print(f"Stop keyword '{found_keywords[0]}' found, trying another path.")
            return None

    # Extract the author name from the page
    author_name = soup.find('h1', {'id': 'firstHeading'}).text
    # Extract the date of birth from the page (if available)
    date_of_birth = soup.find('span', {'class': 'bday'})
    if date_of_birth:
        date_of_birth = date_of_birth.text
        print(f"Author: {author_name}")
        print(f"Date of Birth: {date_of_birth}")
        print(f"URL: {author_page_url}")
        print("------------------------")

        split_name = author_name.split()
        first_name = split_name[0]
        last_name = " ".join(split_name[1:])

        add_author(first_name, last_name, date_of_birth, wiki=author_page_url, verbose=True)

    return None