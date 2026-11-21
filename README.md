# Localizate

## Descripcion:


## Principales funciones: 
    Indica cual es la ruta mas corta al llegar dentro de la universidad para los mechones entre la gente con o sin alguna movilidad reducida.
    Este solo toma rutas que hemos conocido, ademas de no mostrar la ruta por piso 
    El mapa que se muestra no es interactivo



## Instrucciones de instalacion : 
    git clone https://github.com/KiritoGameBoss/La-santa-trinidad.git
    cd La-santa-trinidad

    - Crear y activar un entorno virtual:

        --Linux / macOS:

            python3 -m venv .venv
            source .venv/bin/activate

        --Windows (PowerShell):

            python -m venv .venv
            .venv\Scripts\Activate.ps1

    pip install -r requirements.txt


## Instrucciones de ejecucion: 
    1.Elegir desde donde empezaras la ruta con los edificios seleccionados
    2.Elegir a donde quieres llegar con los edificios seleccionados 
    3.Presionar el boton de "Generar mapa" 

## Tecnologias utilizadas:
    Mapa de la api de Openstreetmap.fr
    Se uso Python como lenguaje principal
    la libreria utilizadas scipy, python-fasthtml , folium y numpy, flask

## Herramientas de inteligencia artificicial:
    Se uso Claude, para corregir problemas errores que aparecian en nuestro mapa 
    Se uso Geminis, para mejorar el interfaz grafica  y para corregir errores

## Equipo de trabajo
    Elian Pantoja encargado de la creacion del mapa e implementarlo en el proyecto
    Esteban Baeza encargado de la creacion de los grafos 
    Ricardo Mendoza encargado de frontend

