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

from src.scrap_hrefs import get_units_hrefs
from src.scrap_infobox import extract_unit_data, find_infobox
from src.utils import fetch_page_content


# 1. Extract: Get the data from the web
def extract_data(url):
    
    units_url = url + "wiki/Unit_(Age_of_Empires_III)"
    unit_list_html = fetch_page_content(units_url)
    href_soup = bs(unit_list_html, "html.parser")

    content = href_soup.find('div', class_='mw-parser-output')
    h2s = content.find_all('h2', recursive=False)
    sections = [h2.find('span', class_='mw-headline', recursive=False).text for h2 in h2s]
    section_unit_hrefs = {section: get_units_hrefs(section, content) for section in sections}

    all_hrefs = [href for sect in section_unit_hrefs.values() for href in sect.values()]

    return all_hrefs

# 2. Transform: Process the data into a structured format
def transform_data(all_hrefs):
    item_types = {
        "text": [
            "Introduced in",
            "Required Home City Card",
            "Hit points",
            "Speed",
            "Line of Sight",
            "XP train bounty",
            "XP kill bounty",
            "Range",
            "Rate of Fire",
            "Train limit",
            "Ability",
            "Special ability",
            "Area of Effect",
            "Requires",
            "Regeneration",
            "Resource amount",
            "Gatherers",
            "Auto gather",
            "Pronunciation",
            "Garrison",
        ],
        "list": ["Type", "Civilization(s)", "Age", "Trained at", "Fatten rate"],
        "dict": ["Cost", "Train time", "Resistance", "Damage", "Bonus damage", "Fatten rate"],
        "ignore": ["Internal name"],
    }

    data = []

    # for url in all_hrefs:
    for url in tqdm(all_hrefs, colour="blue"):
        try:
            unit_html = fetch_page_content(url)
            unit_soup = bs(unit_html, "html.parser")
            infoboxes = unit_soup.find_all("aside", class_="portable-infobox")
            fragment_id = urlparse(url).fragment
            if fragment_id:
                infobox = find_infobox(fragment_id, infoboxes)
            else:
                if len(infoboxes) > 1:
                    raise ValueError("Multiple infoboxes found")
                infobox = infoboxes[0]
            if infobox is None:
                raise ValueError("Infobox not found")
            unit_data = extract_unit_data(infobox, item_types)
            data.append(unit_data)
        except Exception as e:
            print(url)
            print(e)

# 3. Load: Save the data int a json file
def load_data(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Data saved in {filename}")

# ETL Integration
def etl_process(url, output_file):
    print("Starting ETL process...")
    soup = extract_data(url)
    if soup:
        data = transform_data(soup)
        load_data(data, output_file)
    else:
        print("No data to process")

if __name__ == "__main__":
    # Execute the ETL process
    URL = "https://ageofempires.fandom.com/"
    OUTPUT_FILE = "/data/units2.json"

    etl_process(URL, OUTPUT_FILE)