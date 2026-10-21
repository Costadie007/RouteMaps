import json
import math
from datetime import datetime
from pathlib import Path

import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium

# centro inicial do mapa: troque pelas coordenadas da sua região
CENTRO = (-15.78, -47.93)

ARQUIVO_ROTAS = Path("rotas.json")

# velocidades médias em km/h: valores de partida, ajuste ao seu ritmo
VELOCIDADES_KMH = {
    "Caminhada": 5.0,
    "Corrida": 10.0,
    "Bicicleta": 18.0,
}

SATELITE = (
    "https://server.arcgisonline.com/ArcGIS/rest/services/"
    "World_Imagery/MapServer/tile/{z}/{y}/{x}"
)


def haversine_km(a, b):
    raio_terra_km = 6371.0
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * raio_terra_km * math.asin(math.sqrt(h))


def distancia_km(pontos):
    return sum(haversine_km(pontos[i], pontos[i + 1]) for i in range(len(pontos) - 1))


def formatar_tempo(horas):
    minutos_totais = round(horas * 60)
    h, m = divmod(minutos_totais, 60)
    if h:
        return f"{h} h {m:02d} min"
    return f"{m} min"


def carregar_rotas():
    if ARQUIVO_ROTAS.exists():
        return json.loads(ARQUIVO_ROTAS.read_text(encoding="utf-8"))
    return []


def salvar_rotas(rotas):
    ARQUIVO_ROTAS.write_text(
        json.dumps(rotas, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


st.set_page_config(page_title="Planejador de rotas", layout="wide")
st.title("Planejador de rotas")

modo = st.radio("Modo", list(VELOCIDADES_KMH), horizontal=True)

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
    key="mapa",
    height=550,
    use_container_width=True,
    returned_objects=["all_drawings"],
)

pontos = []
for desenho in resultado.get("all_drawings") or []:
    if desenho["geometry"]["type"] == "LineString":
        # o GeoJSON guarda (longitude, latitude), então invertemos para (lat, lon)
        pontos = [(lat, lon) for lon, lat in desenho["geometry"]["coordinates"]]

if len(pontos) >= 2:
    km = distancia_km(pontos)
    horas = km / VELOCIDADES_KMH[modo]

    col1, col2 = st.columns(2)
    col1.metric("Distância", f"{km:.2f} km")
    col2.metric("Tempo estimado", formatar_tempo(horas))

    nome = st.text_input("Nome da rota")
    if st.button("Salvar rota"):
        if not nome.strip():
            st.warning("Dê um nome para a rota antes de salvar.")
        else:
            rotas = carregar_rotas()
            rotas.append({
                "nome": nome.strip(),
                "modo": modo,
                "km": round(km, 3),
                "tempo_h": round(horas, 4),
                "pontos": pontos,
                "criada_em": datetime.now().isoformat(timespec="seconds"),
            })
            salvar_rotas(rotas)
            st.success("Rota salva.")
else:
    st.info("Use a ferramenta de linha no canto do mapa para desenhar a rota.")

st.subheader("Rotas salvas")
rotas_salvas = carregar_rotas()
if not rotas_salvas:
    st.write("Nenhuma rota salva ainda.")
for r in rotas_salvas:
    st.write(
        f"{r['nome']} | {r['modo']} | {r['km']:.2f} km | {formatar_tempo(r['tempo_h'])}"
    )
