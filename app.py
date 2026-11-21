import os, tempfile, uuid
from flask import Flask, jsonify, request, send_from_directory, Response
import campus   # tu archivo campus.py

app = Flask(__name__, static_folder="static")


def perfil_desde_request():
    # el switch del index manda discapacitado=1
    return "movilidad_reducida" if request.args.get("discapacitado") == "1" else "caminante"


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/edificios")
def api_edificios():
    return jsonify(campus.edificios())          # ["B","C","Casino","M","P","T"]


@app.route("/api/ruta")
def api_ruta():
    origen = request.args.get("origen")
    destino = request.args.get("destino")
    perfil = perfil_desde_request()

    ruta = campus.ruta_entre_edificios(origen, destino, perfil)
    if not ruta:
        return jsonify({"ok": False, "error": "No hay ruta disponible para ese perfil."}), 404

    return jsonify({
        "ok": True,
        "metros": round(ruta["metros"]),
        "minutos": max(1, round(ruta["metros"] / campus.VELOCIDAD_M_S / 60)),
        "con_apoyo": len(ruta["tramos_con_apoyo"]) > 0,
        "pasos": campus.describir_ruta(ruta),
    })


@app.route("/mapa")
def mapa():
    """Devuelve el HTML del mapa folium (se muestra dentro de un iframe)."""
    origen = request.args.get("origen")
    destino = request.args.get("destino")
    ruta = None
    if origen and destino:
        ruta = campus.ruta_entre_edificios(origen, destino, perfil_desde_request())

    archivo = os.path.join(tempfile.gettempdir(), f"mapa_{uuid.uuid4().hex}.html")
    campus.crear_mapa(ruta, archivo=archivo)
    with open(archivo, encoding="utf-8") as f:
        html = f.read()
    os.remove(archivo)
    return Response(html, mimetype="text/html")


if __name__ == "__main__":
    app.run(debug=True)