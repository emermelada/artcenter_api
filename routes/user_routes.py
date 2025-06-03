from flask import Blueprint, request, jsonify
import cloudinary.uploader
from utils.auth_decorator import jwt_required
from models import get_connection

user_bp = Blueprint("user", __name__)  # Cambié auth_bp por user_bp

@user_bp.route('/user', methods=['GET'])
@jwt_required  # Asegura que el token esté presente y válido
def get_user_info():
    user_data = request.user  # Los datos del usuario ya están disponibles en request.user
    user_id = user_data.get("id")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT username, urlFotoPerfil FROM Usuario WHERE id = %s", (user_id,))
    user_info = cursor.fetchone()

    if not user_info:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    username, urlFotoPerfil = user_info
    return jsonify({"username": username, "urlFotoPerfil": urlFotoPerfil}), 200


@user_bp.route('/user/username', methods=['PUT'])
@jwt_required  # Asegura que el token esté presente y válido
def update_username():
    user_data = request.user  # Los datos del usuario ya están disponibles en request.user
    user_id = user_data.get("id")
    
    data = request.get_json()
    username = data.get("username")

    if not username:
        return jsonify({"msg": "Se debe proporcionar el nombre de usuario"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE Usuario SET username = %s WHERE id = %s", (username, user_id))

    conn.commit()

    return jsonify({"msg": "Nombre de usuario actualizado correctamente"}), 200


# Ruta para subir la foto de perfil a Cloudinary y actualizar la URL en la base de datos
@user_bp.route('/user/profile-picture', methods=['PUT'])
@jwt_required  # Asegura que el token JWT esté presente y válido
def update_profile_picture():
    user_data = request.user  # Los datos del usuario ya están disponibles en request.user
    user_id = user_data.get("id")
    
    # Obtener la imagen desde la solicitud
    file = request.files.get('file')

    if not file:
        return jsonify({"msg": "No se ha proporcionado una imagen"}), 400

    try:
        # Subir la imagen a Cloudinary
        upload_result = cloudinary.uploader.upload(file)
        image_url = upload_result.get('secure_url')  # Obtenemos la URL segura de la imagen

        # Actualizar la URL de la foto en la base de datos
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Usuario SET urlFotoPerfil = %s WHERE id = %s", (image_url, user_id))
        conn.commit()

        return jsonify({"msg": "Foto de perfil actualizada correctamente", "urlFotoPerfil": image_url}), 200
    except Exception as e:
        return jsonify({"msg": f"Error al subir la imagen: {str(e)}"}), 500
