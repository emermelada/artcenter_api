from flask import Flask, jsonify
from config import Config
from flask_swagger_ui import get_swaggerui_blueprint

from routes.auth_routes import auth_bp            # Blueprint de autenticación
from routes.user_routes import user_bp            # Blueprint de usuario
from routes.categoria_routes import categoria_bp  # Blueprint de categorías
from routes.subcategoria_routes import subcategoria_bp  # Blueprint de subcategorías
from routes.publicacion_routes import publicacion_bp    # Blueprint de publicaciones
from routes.etiqueta_routes import etiqueta_bp            # Blueprint de etiquetas
from routes.comentario_routes import comentario_bp       # Blueprint de comentarios

app = Flask(__name__)
app.config.from_object(Config)

# Registra los blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")       # Rutas de login y registro
app.register_blueprint(user_bp, url_prefix="/api")            # Rutas de usuario
app.register_blueprint(categoria_bp, url_prefix="/api")       # Rutas de categorías
app.register_blueprint(subcategoria_bp, url_prefix="/api")    # Rutas de subcategorías
app.register_blueprint(publicacion_bp, url_prefix="/api")     # Rutas de publicaciones
app.register_blueprint(etiqueta_bp, url_prefix="/api")        # Rutas de etiquetas
app.register_blueprint(comentario_bp, url_prefix="/api")      # Rutas de comentarios

# 1) Ruta donde se mostrará Swagger UI
SWAGGER_URL = '/api/documentacion'
# 2) Ruta al fichero openapi.yaml (servido desde /static)
API_URL = '/static/openapi.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={  # opcionalmente personalizas el UI
        'app_name': "ArtCenter API Docs"
    }
)
# Registramos el blueprint; queda en /api/documentacion(/)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Manejador global para errores 500 (errores del servidor)
@app.errorhandler(500)
def internal_error(error):
    # Puedes añadir más información al mensaje de error si es necesario
    return jsonify({"msg": "Internal server error", "error": str(error)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
