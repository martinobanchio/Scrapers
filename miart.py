"""
Standard scraper utility for the miart gallery list. 

Author: martinobanchio
Date: 12/5/2024
"""

# import the required libraries
import sys
from urllib.request import urlopen, Request
import string
import re
import pandas as pd
from bs4 import BeautifulSoup

YEAR = sys.argv[1]
TARGET_URL = "https://www.miart.it/gallerie-partecipanti/gallerie-" + YEAR + ".html"

def a_processing(a):
    """Preprocessing for a blocks. Checks whether the block is empty, and removes
    all the special characters from the string.

    Args:
        a: an <a> block 

    Returns:
        None if the block is empty, otherwise the processed list of strings.
    """
    if not a.text.strip():
        return None

    raw_text = a.text.split(",")
    for element in raw_text:
        if len(element.translate(str.maketrans('', '', string.punctuation)).strip()) == 0:
            raw_text.remove(element)
    return raw_text

def scraper(url):
    """Scrapes the list of galleries at miart"""

    # make request to the target url
    request = Request(url=url, headers={"User-Agent": "Mozilla/5.0"})
    response = urlopen(request)

    # validate the request
    if response.status != 200:
        return f"status failed with {response.getcode}"
    else:
        # parse the HTML content
        soup = BeautifulSoup(response.read(), "html.parser")
        sections = soup.find_all("section", {"class": "news-detail-text"})
        columns = {"GALLERY": [], "CITY": [], "URL": []}
        cross_block_text = []
        for section in sections:
            for a in section.find_all("a"):

                # Preprocess the block
                text = a_processing(a)
                if text is None:
                    continue

                # Take care of all cases
                if len(text)>3:
                    continue
                elif len(text)<2:
                    cross_block_text.append(text[0])
                    if len(cross_block_text) == 2:
                        gallery, city = cross_block_text
                        columns["GALLERY"].append(gallery.strip())
                        columns["CITY"].append([el.strip() for el in re.split(r".-.", city)])
                        columns["URL"].append(a["href"])
                        cross_block_text = []
                elif len(text) == 3:
                    _, gallery, city = text
                    columns["GALLERY"].append(gallery.strip())
                    columns["CITY"].append([el.strip() for el in re.split(r".-.", city)])
                    columns["URL"].append(a["href"])
                else: 
                    gallery, city = text
                    columns["GALLERY"].append(gallery.strip())
                    columns["CITY"].append([el.strip() for el in re.split(r".-.", city)])
                    columns["URL"].append(a["href"])
        df = pd.DataFrame(columns)
        return df


gallery_list = scraper(TARGET_URL)
gallery_list.to_csv("miart_" + YEAR + "_galleries.csv")
