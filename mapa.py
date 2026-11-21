import folium

# Mapa creado
mapa = folium.Map(
    location=[-33.03486, -71.5952],
    zoom_start=17,
    tiles="https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
    attr="© OpenStreetMap contributors, tiles by OSM France"
)

# Guardar web
mapa.save("mi_mapa.html")

# Guardar web
mapa.save("mi_mapa.html")
