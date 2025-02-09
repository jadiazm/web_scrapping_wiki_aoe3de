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

from pathlib import Path

import requests
from bs4.element import Tag


def norm_string(s):
    return s.strip().replace(" ", "_").lower()


def find_unit_infobox(unit_to_search, infoboxes):

    TARGET_GAME = "Age of Empires III"

    for infobox in infoboxes:

        game_div = infobox.find("div", class_="pi-data-value")

        if not game_div:
            continue

        game = game_div.text.strip()

        # Title verification
        if TARGET_GAME not in game:
            continue

        # Unit name verification
        unit_name = infobox.find("h2")
        if not unit_name:
            continue

        norm_infobox = norm_string(unit_name.text)

        if norm_infobox == unit_to_search:
            return infobox

    raise ValueError("Infobox not found")


def download_unit_icon(infobox: Tag, img_path: str):
    """Downloads the icon of the unit."""
    # Find the icon image element in the infobox element
    icon = infobox.find("img", class_="pi-image-thumbnail", alt="Definitive")
    if icon and icon.has_attr("src"):
        # Fetch the icon image URL
        icon_url = icon["src"]
        try:
            # Download the icon image
            icon_data = requests.get(icon_url).content
            # Get the icon name from the 'data-image-name' attribute
            icon_name = icon["data-image-name"].replace(" ", "_").lower()
            # Save the icon image to the images folder
            with open(Path(img_path) / icon_name, "wb") as file:
                file.write(icon_data)
            print(f"Icono guardado como: '{icon_name}' en '{img_path}'")
        except Exception as e:
            print(f"Error al descargar la imagen: {e}")


def extract_item_vals(item, item_type: str):

    if item_type == "text":
        vals = item.text.strip()
        return vals

    if item_type == "list":
        full_text = ""
        vals = []
        for child in item.children:
            if child.name == "br":
                if full_text:
                    vals.append(full_text.strip())
                    full_text = ""
            else:
                full_text += child.text
        if full_text:
            vals.append(full_text.strip())
        return vals

    elif item_type == "dict":
        grouped_tags = []
        current_group = []

        for child in item.children:
            # Saltar etiquetas con class="image"
            if isinstance(child, Tag) and "image" in (child.get("class") or []):
                continue

            if child.name == "br":
                # Agregar grupo si tiene elementos
                if current_group:
                    grouped_tags.append(current_group)
                    current_group = []
            else:
                # Añadir texto no vacío
                text = child.text.strip()
                if text:
                    current_group.append(text)

        # Agregar el último grupo si no está vacío
        if current_group:
            grouped_tags.append(current_group)

        # Crear diccionario con la información identificada
        vals = {}
        for group in grouped_tags:
            try:
                vals[group[1]] = group[0]
            except IndexError:
                raise ValueError(f"Error extracting dictionary values, present values: {current_group}")
                
        return vals

    elif item_type == "ignore":
        return None

    else:
        raise ValueError(f"Invalid item type: {str(item_type)}")


def get_item_type(val: str) -> str:
    item_types = {
        "text": [
            "Ability",
            "Area of Effect",
            "Auto gather",
            "Bonus damage",
            "Banner army",
            "Garrison",
            "Gatherers",
            "Hit points",
            "Healing",
            "Introduced in",
            "Kill XP",
            "Line of Sight",
            "Pronunciation",
            "Range",
            "Rate of Fire",
            "Regeneration",
            "Resource amount",
            "Required Home City Card",
            "Requires",
            "Special ability",
            "Speed",
            "Train limit",
            "Train XP",
            "XP kill bounty",
            "XP train bounty",
        ],
        "list": [
            "Age",
            "Civilization(s)",
            "Fatten rate",
            "Trained at",
            "Type",
        ],
        "dict": [
            # "Bonus damage",
            "Cost",
            "Damage",
            "Fatten rate",
            "Resistance",
            "Resource bounty",
            "Train time",
        ],
        "ignore": ["Internal name", "Size", "Use"],
    }
    for key, values in item_types.items():
        if val in values:
            return key
    return None


def extract_block_data(block: Tag) -> dict:
    """Extracts the data from a block of the infobox."""

    rows = block.find_all("div", class_="pi-item", recursive=False)
    data = {}

    for row in rows:
        h3 = row.find("h3")
        if h3 is None:
            continue
        label = h3.text
        item = row.find("div", class_="pi-data-value")

        item_type = get_item_type(label)

        if item_type == "ignore":
            continue

        if item_type is None:
            raise ValueError(f"Item type not found for label: '{label}'")

        try:
            values = extract_item_vals(item, item_type)
        except ValueError as e:
            raise ValueError(f"\nError extracting values for label '{label}': {e}")

        # Fill the block data dictionary with the label and its values
        data[label] = values

    return data


def extract_unit_data(infobox: Tag) -> dict:

    # Sections correspond to Groups of information Information, Training, Statistics, etc.
    blocks = infobox.find_all("section")

    unit_name = infobox.find("h2").text.strip()
    
    unit_data = {}
    unit_data["name"] = unit_name

    for block in blocks:
        block_title = block.find("h2").text.strip()

        try:
            block_data = extract_block_data(block)
        except ValueError as e:
            raise ValueError(f"\nError extracting data form block '{block_title}' in infobox '{unit_name}': {e}")
            continue

        # Fill the unit data dictionary with the block title and its data
        unit_data[block_title] = block_data

    return unit_data