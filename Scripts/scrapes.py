import time
import requests
from bs4 import BeautifulSoup
import re

def scrape_wiki(name):
    page = requests.get(f"https://en.wikipedia.org/wiki/{name}")
    soup = BeautifulSoup(page.content, 'html.parser')

    infobox = soup.find(class_="infobox")
    if not infobox:
        return None
    row = infobox.find('th', string='Born')
    if not row:
        return None

    # Extract the birth date from the "Born" row
    birthdate = row.find_next_sibling('td')
    if not birthdate:
        return None
    return birthdate.get_text().strip()

def get_birthdates(authors, delay=0.05):
    birthdates = []

    for author in authors:
        birthdate = scrape_wiki(author)

        regex = r"\((\d{4}-\d{2}-\d{2})\)"
        matches = re.findall(regex, birthdate)

        if matches:
            birthdates.extend(matches)
        else:
            birthdates.extend([None])

        time.sleep(delay)

    return birthdates

if __name__ == '__main__':
    a = get_birthdates(['George Orwell', 'George R.R. Martin', 'Isaac Asimov'])
    print(a)