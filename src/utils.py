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


def fetch_page_content(url):
    """Fetches the HTML content of the page."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text


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
