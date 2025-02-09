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

from bs4 import BeautifulSoup as bs
from tqdm import tqdm

from src.scrap_infobox import extract_unit_data
from src.utils import fetch_page_content, get_section_hrefs


def norm_string(s):
    return s.strip().replace(" ", "_").lower()


def get_units_urls(url) -> list:
    
    units_url = url + "wiki/Unit_(Age_of_Empires_III)"
    unit_list_html = fetch_page_content(units_url)
    href_soup = bs(unit_list_html, "html.parser")

    content = href_soup.find('div', class_='mw-parser-output')
    h2s = content.find_all('h2', recursive=False)
    sections = [h2.find('span', class_='mw-headline', recursive=False).text for h2 in h2s]
    # section_unit_hrefs = {section: get_units_hrefs(section, content) for section in sections}
    units_urls = [
        url + href
        for section in sections
        for href in get_section_hrefs(section, content).values()
    ]

    return units_urls


def get_infoboxes(url, target_game):

    try:

        unit_html = fetch_page_content(url)
        unit_soup = bs(unit_html, "html.parser")
        infoboxes = unit_soup.find_all("aside", class_="portable-infobox")

        valid_infoboxes = []
        for infobox in infoboxes:
            
            game_div = infobox.find("div", class_="pi-data-value")
            
            if not game_div:
                continue

            game = game_div.text.strip()

            if target_game in game:
                valid_infoboxes.append(infobox)

        return valid_infoboxes

    except Exception as e:
        raise Exception(f"Error: {e}")


def export_units_data(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Data saved in {filename}")


def scrape_units_data(url, output_file):

    TARGET_GAME = "Age of Empires III"

    print("Starting extraction process...")

    units_urls = get_units_urls(url)

    print(f"{len(units_urls)} unit URLs available for scraping")

    if not units_urls:
        print("No unit URLs were obtained")
    
    print("Extracting data from the URLs...")
    
    data = []
    for url in tqdm(units_urls, desc="Scraping", unit="units", colour="green"):
        infoboxes = get_infoboxes(url, TARGET_GAME)
        for infobox in infoboxes:
            try:
                unit_data = extract_unit_data(infobox)
                data.append(unit_data)
            except Exception as e:
                print(f"\nExtraction error for url '{url}': {e}")
    
    print(f"Extracted data for {len(data)} units")

    export_units_data(data, output_file)


if __name__ == "__main__":
    # Execute the ETL process
    URL = "https://ageofempires.fandom.com/"
    OUTPUT_FILE = "data/units.json"

    scrape_units_data(URL, OUTPUT_FILE)