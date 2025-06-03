from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import get_connection
from utils.jwt_utils import generate_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("contrasena")
    username = data.get("username")

    if not all([email, password, username]):
        return jsonify({"msg": "Datos incompletos"}), 400

    # Verificar si el email ya existe en la base de datos
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Cuenta WHERE email = %s", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        return jsonify({"msg": "El correo electrónico ya está registrado"}), 409


    hashed = generate_password_hash(password)

    try:
        cursor.execute("INSERT INTO Cuenta (email, contrasena) VALUES (%s, %s)", (email, hashed))
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO Usuario (id, username, urlFotoPerfil) VALUES (%s, %s, %s)", (user_id, username, None))
        conn.commit()
        return jsonify({"msg": "Usuario registrado correctamente"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"msg": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/login', methods=['POST'])
def login():    
    data = request.get_json()
    email = data.get("email")
    password = data.get("contrasena")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, contrasena FROM Cuenta WHERE email = %s", (email,))
    cuenta = cursor.fetchone()

    if not cuenta:
        return jsonify({"msg": "Credenciales incorrectas"}), 401

    user_id, stored_hash = cuenta

    if not check_password_hash(stored_hash, password):
        return jsonify({"msg": "Credenciales incorrectas"}), 401

    # Verifica si es admin o usuario
    cursor.execute("SELECT id FROM Administrador WHERE id = %s", (user_id,))
    admin = cursor.fetchone()
    rol = "admin" if admin else "usuario"

    token = generate_token({"id": user_id, "rol": rol})
    return jsonify({"token": token, "rol": rol, "id": user_id}), 200
