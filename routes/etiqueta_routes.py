from flask import Blueprint, jsonify
from models import get_connection
from utils.auth_decorator import jwt_required

etiqueta_bp = Blueprint("etiqueta", __name__)

@etiqueta_bp.route('/etiquetas', methods=['GET'])
@jwt_required
def obtener_etiquetas():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, nombre FROM Etiqueta")
        etiquetas = cursor.fetchall()

        if not etiquetas:
            return jsonify({"msg": "No se encontraron etiquetas"}), 404

        return jsonify([{"id": e[0], "nombre": e[1]} for e in etiquetas])
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
