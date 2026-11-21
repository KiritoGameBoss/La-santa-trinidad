import folium
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra


def haversine_metros(lat1, lon1, lat2, lon2):
    """Distancia real aproximada en metros entre dos coordenadas (lat, lon)."""
    r = 6371000.0
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2.0) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2.0) ** 2
    return 2.0 * r * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))


# ==========================================
# 1. INSTANCIAS DE NODOS (entradas verdes y quiebres/intersecciones)
# ==========================================
# Cada entrada tiene: id, etiqueta, tipo ("entrada" o "interseccion"), edificio, (lat, lon)
nodos = [
    {"id": 0,  "nombre": "Acceso Edificio Negro",        "tipo": "entrada",      "edificio": "Negro",    "coord": (-33.0342, -71.5988)},
    {"id": 1,  "nombre": "Quiebre Oeste Azul/Rojo",      "tipo": "interseccion", "edificio": None,       "coord": (-33.0346, -71.5979)},
    {"id": 2,  "nombre": "Quiebre Sur Azul",             "tipo": "interseccion", "edificio": None,       "coord": (-33.0351, -71.5968)},
    {"id": 3,  "nombre": "Quiebre Norte Rojo",           "tipo": "interseccion", "edificio": None,       "coord": (-33.0338, -71.5967)},
    {"id": 4,  "nombre": "Entrada Edificio Amarillo",    "tipo": "entrada",      "edificio": "Amarillo", "coord": (-33.0341, -71.5962)},
    {"id": 5,  "nombre": "Convergencia Central-Oeste",   "tipo": "interseccion", "edificio": None,       "coord": (-33.0343, -71.5955)},
    {"id": 6,  "nombre": "Entrada Verde Central-Norte",  "tipo": "entrada",      "edificio": "Verde",    "coord": (-33.0344, -71.5950)},
    {"id": 7,  "nombre": "Entrada Verde Central-Sur",    "tipo": "entrada",      "edificio": "Verde",    "coord": (-33.0353, -71.5948)},
    {"id": 8,  "nombre": "Entrada Verde Central-Este",   "tipo": "entrada",      "edificio": "Verde",    "coord": (-33.0349, -71.5939)},
    {"id": 9,  "nombre": "Entrada Verde Noreste",        "tipo": "entrada",      "edificio": "Verde",    "coord": (-33.0343, -71.5938)},
    {"id": 10, "nombre": "Quiebre Sur-Oeste Naranja",    "tipo": "interseccion", "edificio": None,       "coord": (-33.0365, -71.5952)},
    {"id": 11, "nombre": "Entrada Naranja Norte",        "tipo": "entrada",      "edificio": "Naranja",  "coord": (-33.0353, -71.5936)},
    {"id": 12, "nombre": "Entrada Naranja Este",         "tipo": "entrada",      "edificio": "Naranja",  "coord": (-33.0348, -71.5924)},
    {"id": 13, "nombre": "Entrada Naranja Sur",          "tipo": "entrada",      "edificio": "Naranja",  "coord": (-33.0360, -71.5928)},
    {"id": 14, "nombre": "Entrada Edificio Café",        "tipo": "entrada",      "edificio": "Café",     "coord": (-33.0366, -71.5926)},
    {"id": 15, "nombre": "Convergencia Este Azul/Rojo",  "tipo": "interseccion", "edificio": None,       "coord": (-33.0345, -71.5927)},
    {"id": 16, "nombre": "Quiebre Este Alto",            "tipo": "interseccion", "edificio": None,       "coord": (-33.0339, -71.5912)},
    {"id": 17, "nombre": "Entrada Celeste (Valdés)",     "tipo": "entrada",      "edificio": "Celeste",  "coord": (-33.0335, -71.5902)},
]

coords = np.array([n["coord"] for n in nodos])


# ==========================================
# 2. INSTANCIAS DE ARISTAS (tramos azules y rojos)
# ==========================================
# canal: "azul" (movilidad reducida + caminante) | "rojo" (solo movilidad reducida)
# Si dos nodos se conectan por ambos canales en un tramo convergente, se incluyen ambas aristas.
aristas = [
    # Rama oeste hacia zona amarilla y central
    (0, 1, "azul"), (0, 1, "rojo"),
    (1, 2, "azul"),
    (1, 3, "rojo"),
    (3, 4, "rojo"),
    (2, 5, "azul"),
    (4, 5, "azul"),

    # Bloque central (verde oscuro)
    (5, 6, "azul"),
    (6, 7, "rojo"),
    (6, 9, "rojo"),
    (7, 8, "rojo"),
    (8, 9, "rojo"),

    # Rama sur hacia edificios naranja y café
    (2, 10, "azul"),
    (7, 10, "azul"),
    (10, 13, "azul"),
    (7, 11, "rojo"),
    (11, 12, "rojo"),
    (12, 13, "rojo"),
    (13, 14, "azul"), (13, 14, "rojo"),

    # Rama este hacia edificio celeste (Valdés)
    (9, 15, "azul"),
    (11, 15, "rojo"),
    (12, 15, "rojo"),
    (15, 16, "azul"), (15, 16, "rojo"),
    (16, 17, "azul"), (16, 17, "rojo"),
]


# ==========================================
# 3. CONSTRUCCIÓN DE MATRIZ DISPERSA Y DIJKSTRA (csgraph)
# ==========================================
def construir_grafo(nodos_lista, aristas_lista, perfil="movilidad_reducida", factor_rojo=1.0):
    """
    perfil:
      - "caminante": solo permite aristas 'azul'
      - "movilidad_reducida": permite 'azul' y 'rojo'
    """
    n = len(nodos_lista)
    rows, cols, weights = [], [], []

    for u, v, canal in aristas_lista:
        if perfil == "caminante" and canal == "rojo":
            continue

        lat1, lon1 = nodos_lista[u]["coord"]
        lat2, lon2 = nodos_lista[v]["coord"]
        dist = haversine_metros(lat1, lon1, lat2, lon2)
        peso = dist * (factor_rojo if canal == "rojo" else 1.0)

        # Grafo no dirigido (ida y vuelta)
        rows.extend([u, v])
        cols.extend([v, u])
        weights.extend([peso, peso])

    return csr_matrix((weights, (rows, cols)), shape=(n, n))


def reconstruir_camino(pred, inicio, fin):
    camino = []
    actual = fin
    while actual != -9999 and actual != inicio:
        camino.append(actual)
        actual = pred[actual]
    if actual == inicio:
        camino.append(inicio)
        return camino[::-1]
    return []


origen, destino = 0, 17  # Ej: desde Acceso Edificio Negro (0) hasta Entrada Celeste (17)
perfil_usuario = "movilidad_reducida"  # Cambia a "caminante" para probar restricción azul

grafo = construir_grafo(nodos, aristas, perfil=perfil_usuario)
distancias, predecesores = dijkstra(
    csgraph=grafo,
    directed=False,
    indices=origen,
    return_predecessors=True,
)
ruta_nodos = reconstruir_camino(predecesores, origen, destino)
ruta_coords = [nodos[i]["coord"] for i in ruta_nodos]


# ==========================================
# 4. VISUALIZACIÓN EN FOLIUM SOBRE TU MAPA
# ==========================================
mapa = folium.Map(
    location=[-33.03486, -71.5952],
    zoom_start=17,
    min_zoom=17,
    max_zoom=17,
    tiles="https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
    attr="© OpenStreetMap contributors, tiles by OSM France",
    zoom_control=False,
    scrollWheelZoom=False,
    doubleClickZoom=False,
    touchZoom=False,
    boxZoom=False,
    keyboard=False,
    max_bounds=True,
    min_lat=-33.040,
    max_lat=-33.030,
    min_lon=-71.602,
    max_lon=-71.588,
)

# Dibujar aristas según color (azul / rojo)
for u, v, canal in aristas:
    color_linea = "#1d6fe8" if canal == "azul" else "#d62828"
    folium.PolyLine(
        locations=[nodos[u]["coord"], nodos[v]["coord"]],
        color=color_linea,
        weight=3,
        opacity=0.75,
        tooltip=f"Tramo {canal.upper()}: {u} <-> {v}",
    ).add_to(mapa)

# Resaltar ruta óptima calculada por SciPy
if ruta_coords:
    folium.PolyLine(
        locations=ruta_coords,
        color="#111111",
        weight=6,
        opacity=0.9,
        tooltip=f"Ruta ({perfil_usuario}): {distancias[destino]:.1f} m",
    ).add_to(mapa)

# Dibujar nodos: cuadrados verdes para entradas/salidas, círculos para quiebres
for n in nodos:
    lat, lon = n["coord"]
    if n["tipo"] == "entrada":
        # Representación tipo cuadrado verde usando un polígono pequeño
        d = 0.000045
        cuadrado = [
            [lat - d, lon - d],
            [lat - d, lon + d],
            [lat + d, lon + d],
            [lat + d, lon - d],
        ]
        folium.Polygon(
            locations=cuadrado,
            color="#1b7f2a",
            fill=True,
            fill_color="#2ecc71",
            fill_opacity=0.95,
            weight=2,
            popup=f"[{n['id']}] {n['nombre']}",
        ).add_to(mapa)
    else:
        folium.CircleMarker(
            location=n["coord"],
            radius=4,
            color="#333333",
            fill=True,
            fill_opacity=0.85,
            popup=f"[{n['id']}] Intersección {n['nombre']}",
        ).add_to(mapa)

mapa.save("mapa_algortimo.html")