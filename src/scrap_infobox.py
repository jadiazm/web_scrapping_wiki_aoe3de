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


def find_infobox(fragment_id, infoboxes):
    TARGET_GAME = "Age of Empires III"
    
    fragment_normalized = fragment_id.strip().replace(" ", "_").lower()
    
    for infobox in infoboxes:
        unit_name = infobox.find("h2")
        if not unit_name:
            continue

        unit_name_normalized = unit_name.text.strip().replace(" ", "_").lower()
        game_div = infobox.find("div", class_="pi-data-value")

        if not game_div:
            continue

        game = game_div.text.strip()

        if TARGET_GAME in game and fragment_normalized == unit_name_normalized:
            return infobox
    
    return None


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


def extract_item_vals(item, item_type: str, label: str):

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
                raise ValueError(
                    f"Information for label '{label}' could not be extracted in dict format.\n"
                    f"Present values: '{group}'"
                )
                # print(
                #     f"Information for label '{label}' could not be extracted in dict format.\n"
                #     f"Present values: '{group}'"
                # )
                # return group[0]
        return vals

    elif item_type == "ignore":
        return None

    else:
        raise ValueError(f"Invalid item type: {str(item_type)}")


def get_item_type(val: str, item_types: dict) -> str:
    for key, values in item_types.items():
        if val in values:
            return key
    return None


def extract_block_data(block: Tag, item_types: dict) -> dict:
    """Extracts the data from a block of the infobox."""

    rows = block.find_all("div", class_="pi-item", recursive=False)
    data = {}

    for row in rows:
        h3 = row.find("h3")
        if h3 is None:
            continue
        label = h3.text
        item = row.find("div", class_="pi-data-value")

        item_type = get_item_type(label, item_types)

        if item_type == "ignore":
            continue

        if item_type is None:
            raise ValueError(f"Item type not found for label: '{label}'")

        values = extract_item_vals(item, item_type, label)
        # Fill the block data dictionary with the label and its values
        data[label] = values

    return data


def extract_unit_data(infobox: Tag, item_types: dict) -> dict:

    # Sections correspond to Groups of information Information, Training, Statistics, etc.
    blocks = infobox.find_all("section")

    unit_data = {}

    unit_data["name"] = infobox.find("h2").text.strip()

    for block in blocks:
        block_title = block.find("h2").text.strip()

        block_data = extract_block_data(block, item_types)

        # Fill the unit data dictionary with the block title and its data
        unit_data[block_title] = block_data

    return unit_data