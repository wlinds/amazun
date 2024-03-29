import requests, random
from bs4 import BeautifulSoup
import time # not used, perhaps should set delay somewhere...
import datetime
from flask import Flask, render_template, redirect, url_for

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from books import add_author

# Find authors and date of birth on Wikipedia by
# random crawl through Writers subcategories

# TODO: Check max_author, as it seem to go on past given limit.

def crawl_wikipedia_authors():
    output_messages = []
    crawl_category('https://en.wikipedia.org/wiki/Category:Writers', output_messages)
    return output_messages


def crawl_category(category_url, output_messages, subcategory_hierarchy=[], max_authors=100):
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
            author_info = process_author_page(author_url, output_messages)
            if author_info:
                authors.append(author_info)
                author_count += 1

                if author_count >= max_authors:
                    break

    return authors

def process_author_page(author_url, output_messages):
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
        print(f"Found: {datetime.datetime.now()}")
        print(f"Author: {author_name}")
        print(f"Date of Birth: {date_of_birth}")
        print(f"URL: {author_page_url}")
        print("------------------------")

        split_name = author_name.split()
        first_name = split_name[0]
        last_name = " ".join(split_name[1:])

        if is_valid_date(date_of_birth) == False:
            date_of_birth = None
      
        output_messages.append(f"Author: {author_name}")
        output_messages.append(f"Date of Birth: {date_of_birth}")
        output_messages.append(f"URL: {author_page_url}")
        output_messages.append("------------------------")

        add_author(first_name, last_name, date_of_birth, wiki_link=author_page_url, verbose=True)

    return None

def is_valid_date(date_str):
    try:
        datetime.datetime.strptime(date_str, "%y-%m-%d")
        return True
    except ValueError:
        return False