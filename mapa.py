import folium

# Mapa creado
mapa = folium.Map(
    location=[-33.03486, -71.5952],
    zoom_start=17,
    min_zoom=17,              # zoom mínimo = zoom fijo
    max_zoom=17,              # zoom máximo = zoom fijo
    tiles="https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
    attr="© OpenStreetMap contributors, tiles by OSM France",
    zoom_control=False,       # quita los botones + y -
    scrollWheelZoom=False,
    doubleClickZoom=False,
    touchZoom=False,
    boxZoom=False,
    keyboard=False,
    max_bounds=True,
    min_lat=-33.040, max_lat=-33.030,
    min_lon=-71.602, max_lon=-71.588,
    # sin dragging=False: el mapa se puede mover
)

# Guardar web
mapa.save("mi_mapa.html")