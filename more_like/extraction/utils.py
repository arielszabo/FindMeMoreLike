import requests
from bs4 import BeautifulSoup
import re

def get_ids_from_web_page(html_url):
    """
    Extract movie ids from the html, given an url.
    :param [str] html_url: an url from which to extract movies by their id
    :return: A set of unique movie ids.
    """
    page = requests.get(url=html_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    ids = []
    for link in soup.find_all('a'):
        for id in re.findall(r'tt\d+', str(link)):
            ids.append(id)

    return set(ids)