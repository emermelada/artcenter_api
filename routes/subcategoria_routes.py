from flask import Blueprint, request, jsonify
from models import get_connection
from utils.auth_decorator import jwt_required

subcategoria_bp = Blueprint("subcategoria", __name__)

# Crear una subcategoría (solo administradores)
@subcategoria_bp.route('/subcategorias', methods=['POST'])
@jwt_required
def crear_subcategoria():
    if request.user['rol'] != 'admin':
        return jsonify({"msg": "No autorizado"}), 403

    data = request.get_json()
    id_categoria = data.get("id_categoria")
    nombre = data.get("nombre")
    historia = data.get("historia")
    caracteristicas = data.get("caracteristicas")
    requerimientos = data.get("requerimientos")
    tutoriales = data.get("tutoriales")

    if not id_categoria or not nombre:
        return jsonify({"msg": "id_categoria y nombre son obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM Categoria WHERE id = %s", (id_categoria,))
        categoria_existente = cursor.fetchone()
        if not categoria_existente:
            return jsonify({"msg": "Categoría no encontrada"}), 404

        cursor.execute(
            "SELECT id_subcategoria FROM Subcategoria WHERE id_categoria = %s AND nombre = %s",
            (id_categoria, nombre)
        )
        subcategoria_existente = cursor.fetchone()
        if subcategoria_existente:
            return jsonify({"msg": "Ya existe una subcategoría con ese nombre en esta categoría"}), 409

        cursor.execute(
            "INSERT INTO Subcategoria (id_categoria, id_subcategoria, nombre, historia, caracteristicas, requerimientos, tutoriales) "
            "VALUES (%s, NULL, %s, %s, %s, %s, %s)",
            (id_categoria, nombre, historia, caracteristicas, requerimientos, tutoriales)
        )
        conn.commit()
        return jsonify({"msg": "Subcategoría creada correctamente"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"msg": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# Obtener todas las subcategorías (solo id y nombre)
@subcategoria_bp.route('/subcategorias', methods=['GET'])
@jwt_required
def obtener_subcategorias():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_categoria, id_subcategoria, nombre FROM Subcategoria")
    subcategorias = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify([{
        "id_categoria": sc[0],
        "id_subcategoria": sc[1],
        "nombre": sc[2]
    } for sc in subcategorias])


# Obtener todas las subcategorías de una categoría en particular
@subcategoria_bp.route('/subcategorias/categoria/<int:id_categoria>', methods=['GET'])
@jwt_required
def obtener_subcategorias_por_categoria(id_categoria):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_categoria, id_subcategoria, nombre FROM Subcategoria WHERE id_categoria = %s", (id_categoria,))
    subcategorias = cursor.fetchall()
    cursor.close()
    conn.close()

    if not subcategorias:
        return jsonify({"msg": "No se encontraron subcategorías para esta categoría"}), 404

    return jsonify([{
        "id_categoria": sc[0],
        "id_subcategoria": sc[1],
        "nombre": sc[2]
    } for sc in subcategorias])


# Obtener los detalles de una subcategoría en particular
@subcategoria_bp.route('/subcategorias/<int:id_categoria>/<int:id_subcategoria>', methods=['GET'])
@jwt_required
def obtener_subcategoria_por_id(id_categoria, id_subcategoria):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_categoria, id_subcategoria, nombre, historia, caracteristicas, requerimientos, tutoriales 
        FROM Subcategoria 
        WHERE id_categoria = %s AND id_subcategoria = %s
    """, (id_categoria, id_subcategoria))
    subcategoria = cursor.fetchone()
    cursor.close()
    conn.close()

    if not subcategoria:
        return jsonify({"msg": "Subcategoría no encontrada"}), 404

    return jsonify({
        "id_categoria": subcategoria[0],
        "id_subcategoria": subcategoria[1],
        "nombre": subcategoria[2],
        "historia": subcategoria[3],
        "caracteristicas": subcategoria[4],
        "requerimientos": subcategoria[5],
        "tutoriales": subcategoria[6]
    })
# Eliminar una subcategoría por id_categoria e id_subcategoria (solo admin)
@subcategoria_bp.route('/subcategorias/<int:id_categoria>/<int:id_subcategoria>', methods=['DELETE'])
@jwt_required
def eliminar_subcategoria(id_categoria, id_subcategoria):
    if request.user['rol'] != 'admin':
        return jsonify({"msg": "No autorizado"}), 403

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id_subcategoria FROM Subcategoria WHERE id_categoria = %s AND id_subcategoria = %s",
        (id_categoria, id_subcategoria)
    )
    existente = cursor.fetchone()
    if not existente:
        cursor.close()
        conn.close()
        return jsonify({"msg": "Subcategoría no encontrada"}), 404

    try:
        cursor.execute(
            "DELETE FROM Subcategoria WHERE id_categoria = %s AND id_subcategoria = %s",
            (id_categoria, id_subcategoria)
        )
        conn.commit()
        return jsonify({"msg": "Subcategoría eliminada correctamente"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"msg": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# Editar una subcategoría (solo admin)
@subcategoria_bp.route('/subcategorias/<int:id_categoria>/<int:id_subcategoria>', methods=['PUT'])
@jwt_required
def editar_subcategoria(id_categoria, id_subcategoria):
    if request.user['rol'] != 'admin':
        return jsonify({"msg": "No autorizado"}), 403

    data = request.get_json()
    nombre = data.get("nombre")
    historia = data.get("historia")
    caracteristicas = data.get("caracteristicas")
    requerimientos = data.get("requerimientos")
    tutoriales = data.get("tutoriales")

    if not nombre:
        return jsonify({"msg": "El campo 'nombre' es obligatorio"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id_subcategoria FROM Subcategoria WHERE id_categoria = %s AND id_subcategoria = %s",
        (id_categoria, id_subcategoria)
    )
    existente = cursor.fetchone()
    if not existente:
        cursor.close()
        conn.close()
        return jsonify({"msg": "Subcategoría no encontrada"}), 404

    try:
        cursor.execute(
            """
            UPDATE Subcategoria SET nombre = %s, historia = %s, caracteristicas = %s, 
            requerimientos = %s, tutoriales = %s 
            WHERE id_categoria = %s AND id_subcategoria = %s
            """,
            (nombre, historia, caracteristicas, requerimientos, tutoriales, id_categoria, id_subcategoria)
        )
        conn.commit()
        return jsonify({"msg": "Subcategoría actualizada correctamente"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"msg": str(e)}), 400
    finally:
        cursor.close()
        conn.close()
