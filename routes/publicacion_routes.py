from flask import Blueprint, request, jsonify
import cloudinary.uploader
import pymysql
from pymysql.err import IntegrityError
from utils.auth_decorator import jwt_required
from models import get_connection

publicacion_bp = Blueprint("publicacion", __name__)

# 1) Listar todas las publicaciones (paginado)
@publicacion_bp.route('/publicaciones', methods=['GET'])
@jwt_required
def obtener_publicaciones():
    user_id = request.user['id']              
    page = request.args.get('page', 0, type=int)
    per_page = 20
    offset = page * per_page

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                p.id,
                p.urlContenido,
                p.id_etiqueta,
                e.nombre           AS nombre_etiqueta,
                e.id_categoria,
                e.id_subcategoria,
                (udl.id_usuario IS NOT NULL) AS liked,
                (ugp.id_usuario IS NOT NULL) AS saved,
                p.id_usuario
            FROM Publicacion p
            LEFT JOIN Etiqueta e 
              ON p.id_etiqueta = e.id
            LEFT JOIN Usuario_Da_Like udl 
              ON udl.id_usuario = %s 
             AND udl.id_publicacion = p.id
            LEFT JOIN Usuario_Guarda_Publicacion ugp 
              ON ugp.id_usuario = %s 
             AND ugp.id_publicacion = p.id
            ORDER BY p.fecha_publicacion DESC
            LIMIT %s OFFSET %s
        """, (user_id, user_id, per_page, offset))

        filas = cursor.fetchall()
        if not filas:
            return jsonify({"msg": "No se encontraron publicaciones"}), 404

        resultados = []
        for p in filas:
            resultados.append({
                "id": p[0],
                "urlContenido": p[1],
                "id_etiqueta": p[2],
                "nombre_etiqueta": p[3],
                "id_categoria": p[4],
                "id_subcategoria": p[5],
                "liked": bool(p[6]),
                "saved": bool(p[7]),
                "id_usuario": p[8]
            })

        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"msg": f"Error al obtener publicaciones: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

# 2) Detalle de una publicación por ID (con liked y saved)
@publicacion_bp.route('/publicaciones/<int:id>', methods=['GET'])
@jwt_required
def obtener_publicacion_por_id(id):
    user_id = request.user['id']
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                p.id,
                p.urlContenido,
                p.descripcion,
                p.fecha_publicacion,
                p.likes,
                e.nombre           AS nombre_etiqueta,
                p.id_etiqueta,
                e.id_categoria,
                e.id_subcategoria,
                (udl.id_usuario IS NOT NULL) AS liked,
                (ugp.id_usuario IS NOT NULL) AS saved,
                p.id_usuario
            FROM Publicacion p
            LEFT JOIN Etiqueta e 
              ON p.id_etiqueta = e.id
            LEFT JOIN Usuario_Da_Like udl
              ON udl.id_usuario = %s 
             AND udl.id_publicacion = p.id
            LEFT JOIN Usuario_Guarda_Publicacion ugp
              ON ugp.id_usuario = %s
             AND ugp.id_publicacion = p.id
            WHERE p.id = %s
        """, (user_id, user_id, id))

        p = cursor.fetchone()
        if not p:
            return jsonify({"msg": "Publicación no encontrada"}), 404

        return jsonify({
            "id": p[0],
            "urlContenido": p[1],
            "descripcion": p[2],
            "fecha_publicacion": p[3],
            "likes": p[4],
            "nombre_etiqueta": p[5],
            "id_etiqueta": p[6],
            "id_categoria": p[7],
            "id_subcategoria": p[8],
            "liked": bool(p[9]),
            "saved": bool(p[10]),
            "id_usuario": p[11]
        }), 200

    except Exception as e:
        return jsonify({"msg": f"Error al obtener publicación: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


# 3) Crear publicación (solo usuarios)
@publicacion_bp.route('/publicaciones', methods=['POST'])
@jwt_required
def crear_publicacion():
    if request.user['rol'] == 'admin':
        return jsonify({"msg": "No autorizado"}), 403

    descripcion = request.form.get("descripcion")
    id_etiqueta = request.form.get("id_etiqueta")
    file = request.files.get("file")
    if not file:
        return jsonify({"msg": "No se ha proporcionado una imagen"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        upload_result = cloudinary.uploader.upload(file)
        image_url = upload_result.get('secure_url')

        cursor.execute("""
            INSERT INTO Publicacion (id_usuario, urlContenido, descripcion, id_etiqueta, fecha_publicacion)
            VALUES (%s, %s, %s, %s, NOW())
        """, (request.user['id'], image_url, descripcion, id_etiqueta))
        conn.commit()
        return jsonify({"msg": "Publicación creada correctamente", "urlContenido": image_url}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"msg": f"Error al crear publicación: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

# 4) Mis publicaciones (con liked y saved)
@publicacion_bp.route('/publicaciones/mias', methods=['GET'])
@jwt_required
def obtener_mis_publicaciones():
    user_id = request.user['id']
    page = request.args.get('page', 0, type=int)
    per_page = 20
    offset = page * per_page

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                p.id,
                p.urlContenido,
                p.id_etiqueta,
                e.nombre           AS nombre_etiqueta,
                e.id_categoria,
                e.id_subcategoria,
                (udl.id_usuario IS NOT NULL) AS liked,
                (ugp2.id_usuario IS NOT NULL) AS saved,
                p.id_usuario
            FROM Publicacion p
            LEFT JOIN Etiqueta e 
              ON p.id_etiqueta = e.id
            LEFT JOIN Usuario_Da_Like udl
              ON udl.id_usuario = %s 
             AND udl.id_publicacion = p.id
            LEFT JOIN Usuario_Guarda_Publicacion ugp2
              ON ugp2.id_usuario = %s
             AND ugp2.id_publicacion = p.id
            WHERE p.id_usuario = %s
            ORDER BY p.fecha_publicacion DESC
            LIMIT %s OFFSET %s
        """, (user_id, user_id, user_id, per_page, offset))

        filas = cursor.fetchall()
        if not filas:
            return jsonify({"msg": "No tienes publicaciones"}), 404

        resultados = [{
            "id": p[0],
            "urlContenido": p[1],
            "id_etiqueta": p[2],
            "nombre_etiqueta": p[3],
            "id_categoria": p[4],
            "id_subcategoria": p[5],
            "liked": bool(p[6]),
            "saved": bool(p[7]),
            "id_usuario": p[8]
        } for p in filas]

        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"msg": f"Error al obtener tus publicaciones: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

# 5) Guardar / Quitar guardado (bookmark) publicación
@publicacion_bp.route('/publicaciones/<int:id>/guardar', methods=['POST'])
@jwt_required
def guardar_publicacion(id):
    user_id = request.user['id']
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Usuario_Guarda_Publicacion (id_usuario, id_publicacion)
            VALUES (%s, %s)
        """, (user_id, id))
        conn.commit()
        return jsonify({"msg": "Publicación guardada"}), 201

    except IntegrityError as e:
        if e.args[0] == 1062:
            cursor.execute("""
                DELETE FROM Usuario_Guarda_Publicacion
                WHERE id_usuario = %s AND id_publicacion = %s
            """, (user_id, id))
            conn.commit()
            return jsonify({"msg": "Has quitado el guardado"}), 200
        return jsonify({"msg": f"Error al guardar publicación: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()

# 6) Like / Unlike publicación
@publicacion_bp.route('/publicaciones/<int:id>/like', methods=['POST'])
@jwt_required
def like_publicacion(id):
    user_id = request.user['id']
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Usuario_Da_Like (id_usuario, id_publicacion)
            VALUES (%s, %s)
        """, (user_id, id))
        conn.commit()
        return jsonify({"msg": "Has dado like"}), 201

    except IntegrityError as e:
        if e.args[0] == 1062:
            cursor.execute("""
                DELETE FROM Usuario_Da_Like
                WHERE id_usuario = %s AND id_publicacion = %s
            """, (user_id, id))
            conn.commit()
            return jsonify({"msg": "Has quitado el like"}), 200
        return jsonify({"msg": f"Error al procesar like: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()

# 7) Publicaciones guardadas (con liked y saved siempre True)
@publicacion_bp.route('/publicaciones/guardadas', methods=['GET'])
@jwt_required
def obtener_publicaciones_guardadas():
    user_id = request.user['id']
    page = request.args.get('page', 0, type=int)
    per_page = 20
    offset = page * per_page

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                p.id,
                p.urlContenido,
                p.id_etiqueta,
                e.nombre           AS nombre_etiqueta,
                e.id_categoria,
                e.id_subcategoria,
                (udl.id_usuario IS NOT NULL) AS liked,
                1 AS saved,
                p.id_usuario
            FROM Usuario_Guarda_Publicacion ugp
            JOIN Publicacion p 
              ON ugp.id_publicacion = p.id
            LEFT JOIN Etiqueta e 
              ON p.id_etiqueta = e.id
            LEFT JOIN Usuario_Da_Like udl
              ON udl.id_usuario = %s
             AND udl.id_publicacion = p.id
            WHERE ugp.id_usuario = %s
            ORDER BY p.fecha_publicacion DESC
            LIMIT %s OFFSET %s
        """, (user_id, user_id, per_page, offset))

        filas = cursor.fetchall()
        if not filas:
            return jsonify({"msg": "No tienes publicaciones guardadas"}), 404

        resultados = [{
            "id": p[0],
            "urlContenido": p[1],
            "id_etiqueta": p[2],
            "nombre_etiqueta": p[3],
            "id_categoria": p[4],
            "id_subcategoria": p[5],
            "liked": bool(p[6]),
            "saved": True,
            "id_usuario": p[8]
        } for p in filas]

        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"msg": f"Error al obtener guardadas: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

# 8) Devolver publicaciones con filtro búsqueda
@publicacion_bp.route('/publicaciones/buscar', methods=['GET'])
@jwt_required
def buscar_publicaciones():
    user_id = request.user['id']
    query = request.args.get('q', '', type=str).strip()
    page = request.args.get('page', 0, type=int)
    per_page = 20
    offset = page * per_page

    if not query:
        return jsonify({"msg": "Debes proporcionar un término de búsqueda"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        like_query = f"%{query}%"
        cursor.execute("""
            SELECT 
                p.id,
                p.urlContenido,
                p.id_etiqueta,
                e.nombre AS nombre_etiqueta,
                e.id_categoria,
                e.id_subcategoria,
                (udl.id_usuario IS NOT NULL) AS liked,
                (ugp.id_usuario IS NOT NULL) AS saved,
                p.id_usuario
            FROM Publicacion p
            LEFT JOIN Etiqueta e ON p.id_etiqueta = e.id
            LEFT JOIN Categoria c ON e.id_categoria = c.id
            LEFT JOIN Subcategoria s ON e.id_categoria = s.id_categoria AND e.id_subcategoria = s.id_subcategoria
            LEFT JOIN Usuario u ON p.id_usuario = u.id
            LEFT JOIN Cuenta cu ON u.id = cu.id
            LEFT JOIN Usuario_Da_Like udl ON udl.id_usuario = %s AND udl.id_publicacion = p.id
            LEFT JOIN Usuario_Guarda_Publicacion ugp ON ugp.id_usuario = %s AND ugp.id_publicacion = p.id
            WHERE c.nombre LIKE %s
               OR s.nombre LIKE %s
               OR p.descripcion LIKE %s
               OR u.username LIKE %s
               OR cu.email LIKE %s
            ORDER BY p.fecha_publicacion DESC
            LIMIT %s OFFSET %s
        """, (
            user_id, user_id,
            like_query, like_query, like_query,
            like_query, like_query,
            per_page, offset
        ))

        publicaciones = cursor.fetchall()
        if not publicaciones:
            return jsonify({"msg": "No se encontraron publicaciones que coincidan con la búsqueda"}), 404

        resultados = []
        for p in publicaciones:
            resultados.append({
                "id": p[0],
                "urlContenido": p[1],
                "id_etiqueta": p[2],
                "nombre_etiqueta": p[3],
                "id_categoria": p[4],
                "id_subcategoria": p[5],
                "liked": bool(p[6]),
                "saved": bool(p[7]),
                "id_usuario": p[8]
            })

        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"msg": f"Error al realizar la búsqueda: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

# 9) Eliminar publicación (solo admin o propietario)
@publicacion_bp.route('/publicaciones/<int:id>', methods=['DELETE'])
@jwt_required
def eliminar_publicacion(id):
    user_id = request.user['id']
    user_rol = request.user['rol']

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_usuario FROM Publicacion WHERE id = %s", (id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"msg": "Publicación no encontrada"}), 404

        propietario_id = row[0]

        if user_rol != 'admin' and user_id != propietario_id:
            return jsonify({"msg": "No autorizado para eliminar esta publicación"}), 403

        cursor.execute("DELETE FROM Publicacion WHERE id = %s", (id,))
        conn.commit()

        return jsonify({"msg": "Publicación eliminada correctamente"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"msg": f"Error al eliminar publicación: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
