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

import os

import requests
from bs4 import Tag


def fetch_page_content(url):
    """Fetches the HTML content of the page."""
    response = requests.get(url)
    try:
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP: {e}")


# Save the HTML content of the infobox in a file for each block
def save_infobox_blocks_html(infobox, project_path):
    """Saves the HTML content of the infobox blocks in files."""
    for block in infobox.find_all("section"):
        block_title = block.find("h2").text
        folder_path = os.path.join(project_path, "html", block_title)
        os.makedirs(folder_path, exist_ok=True)
        rows = block.find_all("div", class_="pi-item", recursive=False)
        for row in rows:
            label = row.find("h3").text
            row_path = os.path.join(folder_path, f"{label}.html")
            with open(row_path, "w") as f:
                f.write(str(row))


def get_section_hrefs(section: str, content: Tag) -> dict:
    """
    Get the hyperlinks of the units for each section

    Parameters:
    ---
    section (str): 
        Section of units to get hyperlinks
    content (Tag): 
        HTML content that contains the section of units

    Returns:
    ---
    dict: 
        Dictionary with the unit names as keys and the hyperlinks as values
    """
        
    h2s = content.find_all("h2", recursive=False)
    for h2 in h2s:
        if h2.find("span", class_="mw-headline", recursive=False).text == section:
            ul = h2.find_next_sibling("ul")
            lis = ul.find_all("li", recursive=False)
            section_units = {}
            for li in lis:
                anchor = li.find("a", recursive=False, class_=lambda x: x != "image")
                if anchor is not None:
                    unit_name = anchor.text
                    unit_url = anchor.get("href")
                    section_units[unit_name] = unit_url
            return section_units
