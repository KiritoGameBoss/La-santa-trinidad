import folium

# Crear mapa centrado en Valparaíso
mapa = folium.Map(location=[-33.03486, -71.5952], zoom_start=13)

# Agregar un marcador
folium.Marker([-33.03486, -71.59522], popup="¡Hola Sansano!").add_to(mapa)

# Guardar como archivo web
mapa.save("mi_mapa.html")
