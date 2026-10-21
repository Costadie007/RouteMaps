import folium
import streamlit as st
from folium.plugins import Draw
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

Draw(
    draw_options={
        "polyline": True,
        "polygon": False,
        "rectangle": False,
        "circle": False,
        "marker": False,
        "circlemarker": False,
    },
    edit_options={"edit": True},
).add_to(mapa)

resultado = st_folium(
    mapa,
    height=550,
    use_container_width=True,
    returned_objects=["all_drawings"],
)

pontos = []
for desenho in resultado.get("all_drawings") or []:
    if desenho["geometry"]["type"] == "LineString":
        # o GeoJSON guarda (longitude, latitude), então invertemos para (lat, lon)
        pontos = [(lat, lon) for lon, lat in desenho["geometry"]["coordinates"]]

st.write(f"Pontos desenhados: {len(pontos)}")
st.write(pontos)
