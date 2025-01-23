"""
╔═════════════════════════════════════════════════════════════════════╗
║                      🧩 SCRIPT INFORMATION 🧩                      ║
╠═════════════════════════════════════════════════════════════════════╣
    -  👨‍💻 Author      : Jonathan Diaz
    -  📧 Email       : jonathan.diazm5@gmail.com
    -  📅 Created on  : 2024-12-20
    -  📝 Description : Include functions to get units hyperlinks
╠═════════════════════════════════════════════════════════════════════╣
║  Note: This script is the intellectual property of the author.      ║
║  Its use and modification for educational or personal purposes is   ║
║  permitted, provided that proper credit is given. For any questions ║
║  or comments, please do not hesitate to contact me. 🙌🙌           ║
╚═════════════════════════════════════════════════════════════════════╝
"""

import os
import sys

from bs4 import Tag

project_path = os.path.abspath("..")

sys.path.append(project_path)


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
