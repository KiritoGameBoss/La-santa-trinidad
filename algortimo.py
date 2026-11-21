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
    a = (
        np.sin(dphi / 2.0) ** 2
        + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2.0) ** 2
    )
    return 2.0 * r * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))


# ==========================================
# 1. NODOS (IDs únicos del 0 al 17)
# ==========================================
nodos = [
    {"id": 0,  "nombre": "Acceso Edificio Negro",       "tipo": "entrada",      "edificio": "Negro",    "coord": (-33.035189, -71.597636)},
    {"id": 1,  "nombre": "Quiebre Oeste Azul/Rojo",     "tipo": "interseccion", "edificio": None,       "coord": (-33.035496, -71.597156 )},
    {"id": 2,  "nombre": "Quiebre Sur Azul",            "tipo": "interseccion", "edificio": None,       "coord": (-33.035664, -71.596372)},
    {"id": 3,  "nombre": "Quiebre Norte Rojo",          "tipo": "interseccion", "edificio": None,       "coord": (-33.034875, -71.596187)},
    {"id": 4,  "nombre": "Entrada Edificio Amarillo",   "tipo": "entrada",      "edificio": "Amarillo", "coord": (-33.035286, -71.595930)},
    {"id": 5,  "nombre": "Convergencia Central-Oeste",  "tipo": "interseccion", "edificio": None,       "coord": (-33.035510, -71.595729)},
    {"id": 6,  "nombre": "Entrada Verde Central-Norte", "tipo": "entrada",      "edificio": "Verde",    "coord": (-33.0355, -71.5954)}, #no
    {"id": 7,  "nombre": "Entrada Verde Central-Sur",   "tipo": "entrada",      "edificio": "Verde",    "coord": (-33.0359, -71.5952)},
    {"id": 8,  "nombre": "Entrada Verde Central-Este",  "tipo": "entrada",      "edificio": "Verde",    "coord": (-33.0357, -71.5947)},
    {"id": 9,  "nombre": "Entrada Verde Noreste",       "tipo": "entrada",      "edificio": "Verde",    "coord": (-33.0353, -71.5949)},
    {"id": 10, "nombre": "Quiebre Sur-Oeste Naranja",   "tipo": "interseccion", "edificio": None,       "coord": (-33.0365, -71.5952)},
    {"id": 11, "nombre": "Entrada Naranja Norte",       "tipo": "entrada",      "edificio": "Naranja",  "coord": (-33.0358, -71.5946)},
    {"id": 12, "nombre": "Entrada Naranja Este",        "tipo": "entrada",      "edificio": "Naranja",  "coord": (-33.0357, -71.5938)},
    {"id": 13, "nombre": "Entrada Naranja Sur",         "tipo": "entrada",      "edificio": "Naranja",  "coord": (-33.0363, -71.5944)},
    {"id": 14, "nombre": "Entrada Edificio Café",       "tipo": "entrada",      "edificio": "Café",     "coord": (-33.0370, -71.5942)},
    {"id": 15, "nombre": "Convergencia Este Azul/Rojo", "tipo": "interseccion", "edificio": None,       "coord": (-33.0353, -71.5933)},
    {"id": 16, "nombre": "Quiebre Este Alto",           "tipo": "interseccion", "edificio": None,       "coord": (-33.0353, -71.5933)},
    {"id": 17, "nombre": "Entrada Celeste (Valdés)",    "tipo": "entrada",      "edificio": "Celeste",  "coord": (-33.0351, -71.5929)},
    {"id": 18, "nombre": "intersec",    "tipo": "interseccion",      "edificio": "Naranja",  "coord": (-33.0360,-71.5945)},
    {"id": 19, "nombre": "interseci",    "tipo": "interseccion",      "edificio": None,  "coord": (-33.0360,-71.5937)},
    {"id": 20, "nombre": "interseci",    "tipo": "interseccion",      "edificio": None,  "coord": (-33.0361 ,-71.5957)},
    {"id": 21, "nombre": "interseci",    "tipo": "interseccion",      "edificio": None,  "coord": (-33.0358 , -71.5959)},
    {"id": 22, "nombre": "interseci",    "tipo": "interseccion",      "edificio": None,  "coord": (-33.0355, -71.5939)},


]

# Diccionario rápido para cambiar coordenadas por ID sin equivocarte:
# Ejemplo: nodos_por_id[1]["coord"] = (-33.03455, -71.59785)
nodos_por_id = {n["id"]: n for n in nodos}



# ==========================================
# 2. ARISTAS (tramos azules y rojos)
# ==========================================
# "azul": caminantes y movilidad reducida
# "rojo": solo movilidad reducida
aristas = [
    # Rama oeste hacia zona amarilla y central
    (0, 1, "azul"), (0, 1, "rojo"),
    (1, 2, "azul"),
    (1, 3, "rojo"),
    (3, 4, "rojo"),
    (2, 5, "azul"),
    (4, 5, "azul"),
    (21, 20, "azul"),
    (21, 5, "azul"),
    (20, 7, "azul"),
    (21, 2, "rojo"),

    # Bloque central (verde oscuro)
    (5, 6, "azul"),
    (6, 7, "rojo"),
    (6, 9, "rojo"),
   
    (8, 9, "Rojo"),
    (8, 11, "azul"),
    # Rama sur hacia edificios naranja y café
    (20, 10, "azul"),
    (10, 13, "azul"),
    (7, 11, "azul"),
    (11, 18, "rojo"),
    (18, 13, "rojo"),
    (19, 13, "rojo"),
    (19, 12, "rojo"),
    (18, 12, "rojo"),
    (13, 14, "azul"), (13, 14, "rojo"),

    # Rama este hacia edificio celeste (Valdés)
    (9, 15, "azul"),
    (11, 22, "rojo"),
    (16, 22, "rojo"),
    (12, 15, "rojo"),
    (12, 22, "rojo"),
    (15, 16, "azul"), (15, 16, "rojo"),
    (16, 17, "azul"), (16, 17, "rojo"),
]


# ==========================================
# 3. GRAFO EN SCIPY (csgraph)
# ==========================================
def construir_grafo(nodos_dict, aristas_lista, perfil="movilidad_reducida", factor_rojo=1.0):
    n = len(nodos_dict)
    rows, cols, weights = [], [], []

    for u, v, canal in aristas_lista:
        if perfil == "caminante" and canal == "rojo":
            continue

        lat1, lon1 = nodos_dict[u]["coord"]
        lat2, lon2 = nodos_dict[v]["coord"]
        dist = haversine_metros(lat1, lon1, lat2, lon2)
        peso = dist * (factor_rojo if canal == "rojo" else 1.0)

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


origen, destino = 0, 17
perfil_usuario = "movilidad_reducida"  # Opciones: "movilidad_reducida" o "caminante"

grafo = construir_grafo(nodos_por_id, aristas, perfil=perfil_usuario)
distancias, predecesores = dijkstra(
    csgraph=grafo,
    directed=False,
    indices=origen,
    return_predecessors=True,
)
ruta_nodos = reconstruir_camino(predecesores, origen, destino)
ruta_coords = [nodos_por_id[i]["coord"] for i in ruta_nodos]


# ==========================================
# 4. MAPA EN FOLIUM
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

# Muestra coordenadas [lat, lon] al hacer clic en cualquier parte del mapa
folium.LatLngPopup().add_to(mapa)

# Dibujar aristas azules y rojas
for u, v, canal in aristas:
    color_linea = "#1d6fe8" if canal == "azul" else "#d62828"
    folium.PolyLine(
        locations=[nodos_por_id[u]["coord"], nodos_por_id[v]["coord"]],
        color=color_linea,
        weight=3,
        opacity=0.75,
        tooltip=f"Tramo {canal.upper()}: ID {u} <-> ID {v}",
    ).add_to(mapa)


# Dibujar nodos con su ID visible al pasar el cursor o hacer clic
for n in nodos:
    if n["tipo"] == "paso":
        continue
    lat, lon = n["coord"]
    etiqueta = f"ID {n['id']} — {n['nombre']}"
    if n["tipo"] == "entrada":
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
            tooltip=etiqueta,
            popup=etiqueta,
        ).add_to(mapa)
    else:
        folium.CircleMarker(
            location=n["coord"],
            radius=5,
            color="#333333",
            fill=True,
            fill_opacity=0.9,
            tooltip=etiqueta,
            popup=etiqueta,
        ).add_to(mapa)

mapa.save("mi_mapa.html")