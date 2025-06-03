from flask import Blueprint, request, jsonify
from models import get_connection
from utils.auth_decorator import jwt_required

categoria_bp = Blueprint("categoria", __name__)

@categoria_bp.route('/categorias', methods=['POST'])
@jwt_required
def crear_categoria():
    if request.user['rol'] != 'admin':
        return jsonify({"msg": "No autorizado"}), 403

    data = request.get_json()
    nombre = data.get("nombre")
    descripcion = data.get("descripcion")

    if not nombre or not descripcion:
        return jsonify({"msg": "Todos los campos son obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM Categoria WHERE nombre = %s", (nombre,))
        existente = cursor.fetchone()
        if existente:
            return jsonify({"msg": "Ya existe una categoría con ese nombre"}), 409

        cursor.execute(
            "INSERT INTO Categoria (nombre, descripcion) VALUES (%s, %s)",
            (nombre, descripcion)
        )
        conn.commit()
        return jsonify({"msg": "Categoría creada correctamente"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"msg": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


@categoria_bp.route('/categorias', methods=['GET'])
@jwt_required
def obtener_categorias():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM Categoria")
    categorias = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify([{"id": c[0], "nombre": c[1]} for c in categorias])


@categoria_bp.route('/categorias/<int:id>', methods=['GET'])
@jwt_required
def obtener_categoria_por_id(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, descripcion FROM Categoria WHERE id = %s", (id,))
    categoria = cursor.fetchone()
    cursor.close()
    conn.close()

    if not categoria:
        return jsonify({"msg": "Categoría no encontrada"}), 404

    return jsonify({
        "id": categoria[0],
        "nombre": categoria[1],
        "descripcion": categoria[2]
    })

@categoria_bp.route('/categorias/<int:id>', methods=['DELETE'])
@jwt_required
def eliminar_categoria(id):
    if request.user['rol'] != 'admin':
        return jsonify({"msg": "No autorizado"}), 403

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM Categoria WHERE id = %s", (id,))
    existente = cursor.fetchone()
    if not existente:
        cursor.close()
        conn.close()
        return jsonify({"msg": "Categoría no encontrada"}), 404

    try:
        cursor.execute("DELETE FROM Categoria WHERE id = %s", (id,))
        conn.commit()
        return jsonify({"msg": "Categoría eliminada correctamente"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"msg": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


@categoria_bp.route('/categorias/<int:id>', methods=['PUT'])
@jwt_required
def editar_categoria(id):
    if request.user['rol'] != 'admin':
        return jsonify({"msg": "No autorizado"}), 403

    data = request.get_json()
    nombre = data.get("nombre")
    descripcion = data.get("descripcion")

    if not nombre or not descripcion:
        return jsonify({"msg": "Todos los campos son obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM Categoria WHERE id = %s", (id,))
    existente = cursor.fetchone()
    if not existente:
        cursor.close()
        conn.close()
        return jsonify({"msg": "Categoría no encontrada"}), 404

    try:
        cursor.execute(
            "UPDATE Categoria SET nombre = %s, descripcion = %s WHERE id = %s",
            (nombre, descripcion, id)
        )
        conn.commit()
        return jsonify({"msg": "Categoría actualizada correctamente"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"msg": str(e)}), 400
    finally:
        cursor.close()
        conn.close()
