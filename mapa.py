import folium

#Mapa creado
mapa = folium.Map(location=[-33.03486, -71.5952], zoom_start=13)

#Marcador
folium.Marker([-33.03486, -71.59522], popup="¡Hola Sansano!").add_to(mapa)

# Guardar web
mapa.save("mi_mapa.html")
