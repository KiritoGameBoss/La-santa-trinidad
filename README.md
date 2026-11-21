# Localizate

## Descripcion:
    Una aplicación pensada para mostrar las rutas mas comunes entre edificios transitados
    con un enfoque en mechones. Y tambien las rutas que gente con movilidad reducida puede optar a tomar.

## Objetivos con la ods:
    Nuestro objetivo se alinea con el numero 10 de la ODS Reducción de Desigualdades, ya que nuestra apliaccion esta enfocada en mostrar las rutas comunes entre edificios transitados para que cualquier persona pudea observar que ruta es la mas eficiente.

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
    python app.py
    Entrar al link http://127.0.0.1:5000
    1.Elegir desde donde empezaras la ruta con los edificios seleccionados
    2.Elegir a donde quieres llegar con los edificios seleccionados 
    3.Presionar el boton de "Generar mapa", se asume que la persona camina a 72[m] por minuto

## Tecnologias utilizadas:
    Mapa de la api de Openstreetmap.fr
    Se uso Python como lenguaje principal
    la libreria utilizadas scipy, folium, numpy, flask
    Ademas de usar html para la creacion de la interfaz de usuario.

## Herramientas de inteligencia artificicial:
    Se uso Claude, para corregir problemas errores que aparecian en nuestro mapa 
    Se uso Geminis, para mejorar el interfaz grafica  y para corregir errores

## Recursos externos y codigo reutilizado
    Recursos de IA, el mapa que se muestra, librerias Flask, Scipy... (entre otras)
    No reutilizamos codigo, todo fue hecho hoy

## Equipo de trabajo
    Elian Pantoja encargado de la creacion del mapa e implementarlo en el proyecto
    Esteban Baeza encargado de la creacion de los grafos 
    Ricardo Mendoza encargado de frontend


