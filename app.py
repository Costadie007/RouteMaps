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


def excluir_rota(indice):
    rotas = carregar_rotas()
    rotas.pop(indice)
    salvar_rotas(rotas)
    # volta o seletor para "Nenhuma", senão ele apontaria para uma rota que não existe mais
    st.session_state["rota_escolhida"] = None


st.set_page_config(page_title="Planejador de rotas", layout="wide")
st.title("Planejador de rotas")

modo = st.radio("Modo", list(VELOCIDADES_KMH), horizontal=True)

rotas_salvas = carregar_rotas()
indice_aberto = st.selectbox(
    "Abrir rota salva",
