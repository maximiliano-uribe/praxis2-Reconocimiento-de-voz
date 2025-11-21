from flask import Flask
from routes.main_routes import main_bp
from routes.voz_routes import voz_bp
from routes.clave_routes import clave_bp
from routes.graficos import graficos_bp
import webbrowser, os
from threading import Timer

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_bp)
    app.register_blueprint(voz_bp)
    app.register_blueprint(clave_bp)
    app.register_blueprint(graficos_bp)
    return app


app = create_app()
app.secret_key = os.urandom(24)

def abrir_navegador():
    """Abre automáticamente el navegador en la página principal."""
    webbrowser.open_new("http://127.0.0.1:5000")


if __name__ == "__main__":
    # Abrir navegador 1 segundo después de iniciar el servidor
    Timer(1, abrir_navegador).start()
    app.run(debug=True, use_reloader=False)

