
"""
Campus sin barreras - grafo con coordenadas reales (Hackathon LYOSS USM 2026)
 
Perfiles de usuario:
  - "caminante":           puede usar tramos AZULES, ROJOS y MORADOS
  - "movilidad_reducida":  puede usar tramos AZULES y MORADOS
 
Tramo MORADO: sirve a ambos perfiles, pero para movilidad reducida requiere
APOYO EXTRA, así que la ruta muestra una advertencia.
 
Equivalencia de edificios (antes por color):
  Negro = T | Amarillo = Casino | Verde = B | Naranja = C | Café = P | Celeste = M
 
Uso:  r = ruta_entre_edificios("T", "P", "movilidad_reducida")
      crear_mapa(r)        # genera mi_mapa.html solo con la ruta
      crear_mapa()         # genera el mapa con toda la red
"""
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
 
VELOCIDAD_M_S = 1.2   # SUPUESTO: ~72 m por minuto (declararlo en la documentación)
 
# Qué tramos puede usar cada perfil
PERFILES = {
    "caminante": {"azul", "rojo", "morado"},
    "movilidad_reducida": {"azul", "morado"},
}
 
COLORES = {"azul": "#1d6fe8", "rojo": "#d62828", "morado": "#8e44ad"}
 
 
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
    return float(2.0 * r * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a)))
 
 
# ==========================================
# 1. NODOS (IDs del 0 al 22; el 15 se eliminó y su número no se reutiliza)
# ==========================================
nodos = [
    {"id": 0,  "nombre": "Acceso Edificio T",            "tipo": "entrada",      "edificio": "T",      "coord": (-33.035189, -71.597636)},
    {"id": 1,  "nombre": "Quiebre Oeste Azul/Rojo",      "tipo": "interseccion", "edificio": None,     "coord": (-33.035496, -71.597156)},
    {"id": 2,  "nombre": "Quiebre Sur Azul",             "tipo": "interseccion", "edificio": None,     "coord": (-33.035664, -71.596372)},
    {"id": 3,  "nombre": "Quiebre Norte Rojo",           "tipo": "interseccion", "edificio": None,     "coord": (-33.034875, -71.596187)},
    {"id": 4,  "nombre": "Entrada Casino",               "tipo": "entrada",      "edificio": "Casino", "coord": (-33.035286, -71.595930)},
    {"id": 5,  "nombre": "Convergencia Central-Oeste",   "tipo": "interseccion", "edificio": None,     "coord": (-33.035510, -71.595729)},
    # REVISAR: este nodo tenía un comentario "#no" y coordenadas aproximadas
    {"id": 6,  "nombre": "Entrada B (centro-norte)",     "tipo": "entrada",      "edificio": "B",      "coord": (-33.0355, -71.5954)},
    {"id": 7,  "nombre": "Entrada B (centro-sur)",       "tipo": "entrada",      "edificio": "B",      "coord": (-33.0359, -71.5952)},
    {"id": 8,  "nombre": "Entrada B (centro-este)",      "tipo": "entrada",      "edificio": "B",      "coord": (-33.0357, -71.5947)},
    {"id": 9,  "nombre": "Entrada B (noreste)",          "tipo": "entrada",      "edificio": "B",      "coord": (-33.0353, -71.5949)},
    {"id": 10, "nombre": "Quiebre suroeste (C)",         "tipo": "interseccion", "edificio": None,     "coord": (-33.0365, -71.5952)},
    {"id": 11, "nombre": "Entrada C (norte)",            "tipo": "entrada",      "edificio": "C",      "coord": (-33.0358, -71.5946)},
    {"id": 12, "nombre": "Entrada C (este)",             "tipo": "entrada",      "edificio": "C",      "coord": (-33.0357, -71.5938)},
    {"id": 13, "nombre": "Entrada C (sur)",              "tipo": "entrada",      "edificio": "C",      "coord": (-33.0363, -71.5944)},
    {"id": 14, "nombre": "Entrada Edificio P",           "tipo": "entrada",      "edificio": "P",      "coord": (-33.0370, -71.5942)},
    {"id": 16, "nombre": "Quiebre Este Alto",            "tipo": "interseccion", "edificio": None,     "coord": (-33.0353, -71.5933)},
    {"id": 17, "nombre": "Entrada Edificio M (Valdés)",  "tipo": "entrada",      "edificio": "M",      "coord": (-33.0351, -71.5929)},
    {"id": 18, "nombre": "Intersección interior C (18)", "tipo": "interseccion", "edificio": "C",      "coord": (-33.0360, -71.5945)},
    {"id": 19, "nombre": "Intersección 19",              "tipo": "interseccion", "edificio": None,     "coord": (-33.0360, -71.5937)},
    {"id": 20, "nombre": "Intersección 20",              "tipo": "interseccion", "edificio": None,     "coord": (-33.0361, -71.5957)},
    {"id": 21, "nombre": "Intersección 21",              "tipo": "interseccion", "edificio": None,     "coord": (-33.0358, -71.5959)},
    {"id": 22, "nombre": "Intersección 22",              "tipo": "interseccion", "edificio": None,     "coord": (-33.0355, -71.5939)},
]
 
# Para cambiar una coordenada por ID: nodos_por_id[1]["coord"] = (-33.03455, -71.59785)
nodos_por_id = {n["id"]: n for n in nodos}
 
 
# ==========================================
# 2. ARISTAS (tramos azules y rojos)
# ==========================================
# "azul":   lo pueden usar caminantes y movilidad reducida
# "rojo":   lo pueden usar solo caminantes
# "morado": lo pueden usar ambos, pero movilidad reducida necesita apoyo extra
# Si un mismo tramo sirve a ambos sin ayuda, basta con ponerlo en azul.
aristas = [
    # Rama oeste hacia zona Casino y central
    (0, 1, "morado"),   # solo era rojo: con apoyo extra pueden pasar quienes tienen movilidad reducida
    (1, 2, "azul"),
    (1, 3, "rojo"),
    (3, 4, "rojo"),
    (2, 5, "azul"),
    (4, 5, "azul"),
    (21, 20, "azul"),
    (21, 5, "azul"),
    (20, 7, "azul"),
    (21, 2, "rojo"),
 
    # Edificio B
    (5, 6, "azul"),
    (6, 7, "rojo"),
    (6, 9, "rojo"),
    (8, 9, "rojo"),
    (8, 11, "azul"),
 
    # Rama sur hacia edificios C y P
    (20, 10, "azul"),
    (10, 13, "azul"),
    (7, 11, "azul"),
    (11, 18, "rojo"),
    (18, 13, "rojo"),
    (19, 13, "rojo"),
    (19, 12, "rojo"),
    (18, 12, "rojo"),
    (13, 14, "azul"),
 
    # Rama este hacia edificio M (Valdés)
    (9, 16, "azul"),     # antes pasaba por el nodo 15 (eliminado)
    (11, 22, "rojo"),
    (16, 22, "rojo"),
    (12, 16, "rojo"),    # antes pasaba por el nodo 15 (eliminado)
    (12, 22, "rojo"),
    (16, 17, "azul"),
]
 
 
# ==========================================
# 3. GRAFO (scipy csgraph)
# ==========================================
def construir_grafo(nodos_dict, aristas_lista, perfil="movilidad_reducida",
                    factor_rojo=1.0, factor_morado=1.0):
    """Matriz de pesos en metros. Un tramo repetido (azul y rojo) cuenta UNA vez."""
    permitidos = PERFILES[perfil]
    n = max(nodos_dict) + 1   # los IDs se usan como índices de la matriz (el 15 queda vacío)
    pesos = {}
    for u, v, canal in aristas_lista:
        canal = canal.strip().lower()
        if canal not in permitidos:
            continue
        lat1, lon1 = nodos_dict[u]["coord"]
        lat2, lon2 = nodos_dict[v]["coord"]
        d = haversine_metros(lat1, lon1, lat2, lon2)
        if canal == "rojo":
            d *= factor_rojo
        elif canal == "morado":
            d *= factor_morado   # >1 para preferir rutas sin apoyo extra cuando hay alternativa
        clave = (min(u, v), max(u, v))
        pesos[clave] = min(pesos.get(clave, float("inf")), d)   # evita sumar duplicados
 
    rows, cols, weights = [], [], []
    for (u, v), w in pesos.items():
        rows += [u, v]
        cols += [v, u]
        weights += [w, w]
    return csr_matrix((weights, (rows, cols)), shape=(n, n))
 
 
def reconstruir_camino(pred, inicio, fin):
    camino = []
    actual = fin
    while actual != -9999 and actual != inicio:
        camino.append(int(actual))
        actual = pred[actual]
    if actual == inicio:
        camino.append(int(inicio))
        return camino[::-1]
    return []
 
 
def requiere_apoyo(u, v, perfil):
    """True si el tramo u-v solo puede recorrerse como MORADO para ese perfil
    y el perfil es de movilidad reducida (los caminantes no necesitan apoyo)."""
    if perfil != "movilidad_reducida":
        return False
    canales = {c.strip().lower() for a, b, c in aristas
               if {a, b} == {u, v} and c.strip().lower() in PERFILES[perfil]}
    return canales == {"morado"}
 
 
def ruta_entre_nodos(origen, destino, perfil="movilidad_reducida"):
    """Devuelve (lista de IDs, metros) o None si no hay ruta para ese perfil."""
    grafo = construir_grafo(nodos_por_id, aristas, perfil=perfil)
    dist, pred = dijkstra(grafo, directed=False, indices=origen, return_predecessors=True)
    camino = reconstruir_camino(pred, origen, destino)
    if not camino:
        return None
    return camino, float(dist[destino])
 
 
# ==========================================
# 4. RUTA ENTRE EDIFICIOS (lo que elige el usuario en los menús)
# ==========================================
def edificios():
    """Lista de edificios disponibles para los menús desplegables."""
    return sorted({n["edificio"] for n in nodos if n["tipo"] == "entrada"})
 
 
def entradas_de(edificio):
    return [n["id"] for n in nodos if n["tipo"] == "entrada" and n["edificio"] == edificio]
 
 
def ruta_entre_edificios(origen_ed, destino_ed, perfil="movilidad_reducida"):
    """Mejor ruta entre cualquier entrada del origen y cualquiera del destino."""
    if origen_ed == destino_ed:
        return None
    mejor = None
    for o in entradas_de(origen_ed):
        for d in entradas_de(destino_ed):
            r = ruta_entre_nodos(o, d, perfil)
            if r and (mejor is None or r[1] < mejor["metros"]):
                tramos = [(r[0][i], r[0][i + 1]) for i in range(len(r[0]) - 1)]
                apoyo = [t for t in tramos if requiere_apoyo(*t, perfil)]
                mejor = {"nodos": r[0], "metros": r[1], "perfil": perfil,
                         "origen": origen_ed, "destino": destino_ed,
                         "tramos_con_apoyo": apoyo}
    return mejor
 
 
def describir_ruta(ruta):
    """Texto paso a paso a partir de los nodos recorridos."""
    ids = ruta["nodos"]
    minutos = max(1, round(ruta["metros"] / VELOCIDAD_M_S / 60))
    lineas = [
        f"Ruta {ruta['origen']} → {ruta['destino']} ({ruta['perfil']}): "
        f"{round(ruta['metros'])} m, ~{minutos} min a pie",
        f"Sal por: {nodos_por_id[ids[0]]['nombre']}",
    ]
    for i in range(len(ids) - 1):
        a, b = nodos_por_id[ids[i]], nodos_por_id[ids[i + 1]]
        m = haversine_metros(*a["coord"], *b["coord"])
        nota = "  [REQUIERE APOYO EXTRA]" if (ids[i], ids[i + 1]) in ruta["tramos_con_apoyo"] else ""
        lineas.append(f"{i + 1}. {a['nombre']} → {b['nombre']} ({round(m)} m){nota}")
    lineas.append(f"Llegas por: {nodos_por_id[ids[-1]]['nombre']}")
    if ruta["tramos_con_apoyo"]:
        lineas.append("ATENCIÓN: esta ruta incluye tramos que requieren apoyo extra "
                      "(ayuda de otra persona) para personas con movilidad reducida.")
    return lineas
 
 
def diagnostico():
    """Pares de edificios SIN ruta para cada perfil (sirve para detectar tramos que faltan)."""
    resultado = {}
    for perfil in PERFILES:
        resultado[perfil] = [
            (a, b) for a in edificios() for b in edificios()
            if a < b and not ruta_entre_edificios(a, b, perfil)
        ]
    return resultado
 
 
# ==========================================
# 5. MAPA EN FOLIUM
# ==========================================
def crear_mapa(ruta=None, archivo="mi_mapa.html"):
    import folium   # se importa aquí para poder probar el grafo sin folium
 
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
 
    # Muestra [lat, lon] al hacer clic (sirve para afinar coordenadas)
    folium.LatLngPopup().add_to(mapa)
 
    if ruta:
        # Con una ruta calculada solo se muestran la ruta y sus puntos
        ids = ruta["nodos"]
        for u, v in zip(ids[:-1], ids[1:]):
            apoyo = (u, v) in ruta["tramos_con_apoyo"]
            folium.PolyLine(
                locations=[nodos_por_id[u]["coord"], nodos_por_id[v]["coord"]],
                color=COLORES["morado"] if apoyo else "#2ecc71",
                weight=8,
                opacity=0.95,
                tooltip=("Requiere apoyo extra" if apoyo else
                         f"Ruta {ruta['origen']} → {ruta['destino']}: {round(ruta['metros'])} m"),
            ).add_to(mapa)
        nodos_visibles = [nodos_por_id[i] for i in ids]
    else:
        # Sin ruta se muestra toda la red (útil para revisar el grafo)
        for u, v, canal in aristas:
            canal = canal.strip().lower()
            folium.PolyLine(
                locations=[nodos_por_id[u]["coord"], nodos_por_id[v]["coord"]],
                color=COLORES.get(canal, "#888888"),
                weight=3,
                opacity=0.75,
                tooltip=f"Tramo {canal.upper()}: ID {u} <-> ID {v}",
            ).add_to(mapa)
        nodos_visibles = nodos
 
    # Nodos
    for n in nodos_visibles:
        lat, lon = n["coord"]
        etiqueta = f"ID {n['id']} — {n['nombre']}"
        if n["tipo"] == "entrada":
            d = 0.000045
            folium.Polygon(
                locations=[[lat - d, lon - d], [lat - d, lon + d],
                           [lat + d, lon + d], [lat + d, lon - d]],
                color="#1b7f2a", fill=True, fill_color="#2ecc71",
                fill_opacity=0.95, weight=2, tooltip=etiqueta, popup=etiqueta,
            ).add_to(mapa)
        else:
            folium.CircleMarker(
                location=n["coord"], radius=5, color="#333333",
                fill=True, fill_opacity=0.9, tooltip=etiqueta, popup=etiqueta,
            ).add_to(mapa)
 
    mapa.save(archivo)
    return archivo
 