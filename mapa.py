import folium

mapa = folium.Map(
    location=[-33.03486, -71.5952],
    zoom_start=17,
    min_zoom=17,              # zoom fijo
    max_zoom=17,
    tiles="https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
    attr="© OpenStreetMap contributors, tiles by OSM France",
    zoom_control=False,       # quita los botones + y -
    scrollWheelZoom=False,    # sin zoom con la rueda
    doubleClickZoom=False,    # sin zoom con doble clic
    touchZoom=False,          # sin zoom con pellizco (celular)
    boxZoom=False,            # sin zoom con Shift + arrastrar
    keyboard=False,           # sin zoom ni movimiento con el teclado (flechas, + y -)
    max_bounds=True,
    min_lat=-33.040, max_lat=-33.030,
    min_lon=-71.602, max_lon=-71.588,
    # el mapa se puede arrastrar con el mouse dentro de esos límites
)

mapa.save("mi_mapa.html")