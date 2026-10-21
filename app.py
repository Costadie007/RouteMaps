import folium
import streamlit as st
from streamlit_folium import st_folium

# centro inicial do mapa: troque pelas coordenadas da sua região
CENTRO = (-15.78, -47.93)

SATELITE = (
    "https://server.arcgisonline.com/ArcGIS/rest/services/"
    "World_Imagery/MapServer/tile/{z}/{y}/{x}"
)

st.set_page_config(page_title="Planejador de rotas", layout="wide")
st.title("Planejador de rotas")

mapa = folium.Map(location=CENTRO, zoom_start=16, tiles=None)
folium.TileLayer(SATELITE, attr="Esri World Imagery", name="Satélite").add_to(mapa)

st_folium(mapa, height=550, use_container_width=True)
