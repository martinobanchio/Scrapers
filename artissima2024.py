"""
Standard scraper utility for the Artissima 2024 gallery list

Author: martinobanchio
Date: 11/10/2024
"""

# import the required libraries
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import pandas as pd

TARGET_URL = "https://www.artissima.art/elenco-espositori/"


def scraper(url):
    """Scrapes the list of galleries at artissima 2024"""

    # make request to the target url
    request = Request(url=url, headers={"User-Agent": "Mozilla/5.0"})
    response = urlopen(request)

    # validate the request
    if response.status != 200:
        return f"status failed with {response.getcode}"
    else:
        # parse the HTML content
        soup = BeautifulSoup(response.read(), "html.parser")

        table = soup.find("table", id="tablepress-175")

        # routine to collect all column names
        # initializes the dataframe as well
        columns = {}
        for element in table.find("thead").find_all("th"):
            columns[element.text] = []
        columns["URL"] = []
        data = pd.DataFrame(columns)

        errors = 0
        for row in table.find("tbody").find_all("tr"):
            try:
                column = []
                for columns in row.find_all("td"):
                    column.append(columns.text)
                column.append(row.find("a")["href"])
                data = pd.concat(
                    [data, pd.DataFrame([column], columns=data.columns)],
                    ignore_index=True,
                )
            except ValueError:
                errors += 1
        print(f"errors: {errors}")
    return data


gallery_list = scraper(TARGET_URL)
gallery_list.to_csv("artissima_2024_galleries.csv")
