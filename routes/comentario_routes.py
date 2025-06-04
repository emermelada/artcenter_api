from flask import Blueprint, request, jsonify
from models import get_connection
from utils.auth_decorator import jwt_required

comentario_bp = Blueprint("comentario", __name__)

# 1) Obtener todos los comentarios de una publicación
@comentario_bp.route('/publicaciones/<int:id_publicacion>/comentarios', methods=['GET'])
@jwt_required
def obtener_comentarios_por_publicacion(id_publicacion):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Verificamos que la publicación exista
        cursor.execute("SELECT id FROM Publicacion WHERE id = %s", (id_publicacion,))
        publicacion = cursor.fetchone()
        if not publicacion:
            return jsonify({"msg": "Publicación no encontrada"}), 404

        # Obtenemos todos los comentarios y el username del autor
        cursor.execute("""
            SELECT c.id,
                   c.id_usuario,
                   u.username,
                   c.contenido,
                   c.fecha_publicacion
            FROM Comentario c
            JOIN Usuario u ON c.id_usuario = u.id
            WHERE c.id_publicacion = %s
            ORDER BY c.fecha_publicacion ASC
        """, (id_publicacion,))
        filas = cursor.fetchall()
        comentarios = []
        for fila in filas:
            comentarios.append({
                "id": fila[0],
                "id_usuario": fila[1],
                "username": fila[2],
                "contenido": fila[3],
                "fecha_publicacion": fila[4]
            })

        return jsonify(comentarios), 200

    except Exception as e:
        return jsonify({"msg": f"Error al obtener comentarios: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


# 2) Crear un nuevo comentario en una publicación
@comentario_bp.route('/publicaciones/<int:id_publicacion>/comentarios', methods=['POST'])
@jwt_required
def crear_comentario(id_publicacion):
    data = request.get_json()
    contenido = data.get("contenido")

    if not contenido or contenido.strip() == "":
        return jsonify({"msg": "El campo 'contenido' es obligatorio"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Verificamos que la publicación exista
        cursor.execute("SELECT id FROM Publicacion WHERE id = %s", (id_publicacion,))
        publicacion = cursor.fetchone()
        if not publicacion:
            return jsonify({"msg": "Publicación no encontrada"}), 404

        # Insertamos el comentario
        cursor.execute("""
            INSERT INTO Comentario (id_usuario, id_publicacion, contenido, fecha_publicacion)
            VALUES (%s, %s, %s, NOW())
        """, (request.user['id'], id_publicacion, contenido))
        conn.commit()

        return jsonify({"msg": "Comentario creado correctamente", "id_comentario": cursor.lastrowid}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"msg": f"Error al crear comentario: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


# 3) Eliminar un comentario (solo si eres el autor o un administrador)
@comentario_bp.route('/comentarios/<int:id_comentario>', methods=['DELETE'])
@jwt_required
def eliminar_comentario(id_comentario):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Verificamos que el comentario exista
        cursor.execute("SELECT id, id_usuario FROM Comentario WHERE id = %s", (id_comentario,))
        comentario = cursor.fetchone()
        if not comentario:
            return jsonify({"msg": "Comentario no encontrado"}), 404

        # Comprobamos si el usuario es el autor del comentario o un administrador
        if comentario[1] != request.user['id'] and request.user['rol'] != 'admin':
            return jsonify({"msg": "No autorizado"}), 403

        # Eliminamos el comentario
        cursor.execute("DELETE FROM Comentario WHERE id = %s", (id_comentario,))
        conn.commit()
        return jsonify({"msg": "Comentario eliminado correctamente"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"msg": f"Error al eliminar comentario: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

