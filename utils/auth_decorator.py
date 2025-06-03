from functools import wraps
from flask import request, jsonify
from utils.jwt_utils import verify_token

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization")

        if not auth or not auth.startswith("Bearer "):
            return jsonify({"msg": "Token requerido"}), 401

        token = auth.split(" ")[1]
        data = verify_token(token)

        if not data:
            return jsonify({"msg": "Token inválido o expirado"}), 401

        request.user = data
        return f(*args, **kwargs)
    return decorated
