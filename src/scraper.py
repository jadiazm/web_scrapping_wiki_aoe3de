from pathlib import Path

import requests
from bs4.element import Tag, NavigableString


def fetch_page_content(url):
    """Fetches the HTML content of the page."""
    response = requests.get(url)
    response.raise_for_status()
    # Raises an error for bad responses (e.g., 404, 500)
    return response.text


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


def extract_feat_values(elements: Tag, is_st_label: bool = False) -> dict | list | str:

    if is_st_label:
        # Extract the features of the cost
        feat_labels = []
        feat_vals = []
        for feat in elements.children:
            # Si el elemento no es una etiqueta <a> y es un texto, lo agregamos
            if isinstance(feat, Tag) and feat.name == "a" and feat.has_attr("title"):
                feat_labels.append(feat.get_text(strip=True))
            elif isinstance(feat, NavigableString) and feat.strip():
                feat_vals.append(feat.strip())
            else:
                continue

        if feat_labels:
            values = dict(zip(feat_labels, feat_vals))
        else:
            values = {feat_vals[i + 1]: feat_vals[i] for i in range(0, len(feat_vals), 2)}

    else:
        values = []
        n_tags_a = 0
        for a in elements.find_all("a", recursive=False):
            if a.has_attr("title"):
                n_tags_a += 1
                text = a.get_text(strip=False)
                # Buscar el tag <small> adyacente
                next_tag = a.find_next_sibling()
                if next_tag and next_tag.name == "small":
                    text += " " + next_tag.get_text(strip=False)
                values.append(text.strip())

        # If there are no <a> tags, get the text of the element and save it as value
        if n_tags_a == 0:
            text = elements.get_text(strip=False)
            values = text.strip()

    return values


def extract_block_data(block: Tag) -> dict:
    """Extracts the data from a block of the infobox."""
    data = {}

    statistic_labels = [
        "Cost",
        "Resistance",
        "Damage",
        "Bonus damage",
        "Train time",
    ]

    for row in block.find_all("div", class_="pi-item", recursive=False):
        label = row.find("h3").text
        is_st_label = label in statistic_labels

        elements = row.find("div", class_="pi-data-value")

        values = extract_feat_values(elements, is_st_label)

        # Fill the block data dictionary with the label and its values
        data[label] = values

        print("label: ", label)
        print("value_type: ", type(values).__name__)
        print("values: ", values)
        print()

    return data


def extract_unit_data(infobox: Tag):

    # Sections correspond to Groups of information Information, Training, Statistics, etc.
    blocks = infobox.find_all("section")

    unit_data = {}

    for block in blocks:
        block_title = block.find("h2").text

        block_data = extract_block_data(block)

        # Fill the unit data dictionary with the block title and its data
        unit_data[block_title] = block_data

    return unit_data
