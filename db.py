import requests
from bs4 import BeautifulSoup
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Definir base para SQLAlchemy
Base = declarative_base()

class Pokemon(Base):
    __tablename__ = 'pokemon'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    types = Column(String, nullable=False)
    stats = Column(String, nullable=True)  # JSON string for stats

# Crear base de datos SQLite
engine = create_engine('sqlite:///pokemon.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Web scraping
url = "https://example.com/pokemon-list"  # Reemplazar con la URL real
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extraer datos (ejemplo ficticio)
pokemon_list = soup.find_all('div', class_='pokemon-card')  # Cambia según la estructura

for card in pokemon_list:
    name = card.find('h2').text.strip()
    types = ", ".join([t.text for t in card.find_all('span', class_='type')])
    stats = {"HP": 60, "Attack": 80}  # Sustituir con datos reales

    # Guardar en la base de datos
    new_pokemon = Pokemon(name=name, types=types, stats=str(stats))
    session.add(new_pokemon)

# Confirmar los cambios
session.commit()
