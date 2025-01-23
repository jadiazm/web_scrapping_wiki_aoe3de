"""
╔═════════════════════════════════════════════════════════════════════╗
║                      🧩 SCRIPT INFORMATION 🧩                      ║
╠═════════════════════════════════════════════════════════════════════╣
    -  👨‍💻 Author      : Jonathan Diaz
    -  📧 Email       : jonathan.diazm5@gmail.com
    -  📅 Created on  : 2024-12-20
    -  📝 Description : 
╠═════════════════════════════════════════════════════════════════════╣
║  Note: This script is the intellectual property of the author.      ║
║  Its use and modification for educational or personal purposes is   ║
║  permitted, provided that proper credit is given. For any questions ║
║  or comments, please do not hesitate to contact me. 🙌🙌           ║
╚═════════════════════════════════════════════════════════════════════╝
"""

import json
import os
import sys

project_path = os.path.abspath(".")

sys.path.append(project_path)

from urllib.parse import urlparse

from bs4 import BeautifulSoup as bs
from tqdm import tqdm

from src.scrap_hrefs import get_section_hrefs
from src.scrap_infobox import extract_unit_data, find_infobox
from src.utils import fetch_page_content


def norm_string(s):
    return s.strip().replace(" ", "_").lower()


# 1. Extract: Get the data from the web
def get_units_urls(url) -> list:
    
    units_url = url + "wiki/Unit_(Age_of_Empires_III)"
    unit_list_html = fetch_page_content(units_url)
    href_soup = bs(unit_list_html, "html.parser")

    content = href_soup.find('div', class_='mw-parser-output')
    h2s = content.find_all('h2', recursive=False)
    sections = [h2.find('span', class_='mw-headline', recursive=False).text for h2 in h2s]
    # section_unit_hrefs = {section: get_units_hrefs(section, content) for section in sections}
    units_urls = {
        unit: url + href
        for section in sections
        for unit, href in get_section_hrefs(section, content).items()
    }

    return units_urls


# 2. Transform: Process the data into a structured format
def scrape_unit_data(unit, units_urls) -> list:

    TARGET_GAME = "Age of Empires III"

    try:

        url = units_urls[unit]

        unit_html = fetch_page_content(url)
        unit_soup = bs(unit_html, "html.parser")
        infoboxes = unit_soup.find_all("aside", class_="portable-infobox")

        fragment_id = urlparse(url).fragment

        norm_fragment_id = norm_string(fragment_id) if fragment_id else None
        norm_target_game = norm_string(TARGET_GAME)
        norm_unit = norm_string(unit)

        unit_to_search = (norm_unit if norm_fragment_id == norm_target_game else norm_fragment_id) or norm_unit

        infobox = find_infobox(unit_to_search, infoboxes)

        unit_data = extract_unit_data(infobox)

        return unit_data

    except Exception as e:
        raise Exception(f"Error: {e}")


# 3. Load: Save the data int a json file
def load_data(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Data saved in {filename}")


# ETL Integration
def etl_process(url, output_file):
    print("Starting extraction process...")
    units_urls = get_units_urls(url)
    print(f"{len(units_urls)} unit URLs available for scraping")
    if not units_urls:
        print("No unit URLs were obtained")
    
    # for unit, url in tqdm(all_hrefs.items(), colour="blue"):
    print("Extracting data from the URLs...")
    data = {}
    for unit in units_urls.keys():
        try:
            data[unit] = scrape_unit_data(unit, units_urls)
        except Exception as e:
            print(f"Extraction error for unit: {unit} - {e}")
    print(f"Extracted data for {len(data)} units")
    load_data(data, output_file)

if __name__ == "__main__":
    # Execute the ETL process
    URL = "https://ageofempires.fandom.com/"
    OUTPUT_FILE = "data/units.json"

    etl_process(URL, OUTPUT_FILE)
