CREATE DATABASE IF NOT EXISTS artcenterDB;
USE artcenterDB;

-- Entidad Cuenta
CREATE TABLE Cuenta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
);

-- Entidad Usuario
CREATE TABLE Usuario (
    id INT PRIMARY KEY,
    urlFotoPerfil VARCHAR(2083),
    username VARCHAR(100) NOT NULL,
    CHECK (urlFotoPerfil REGEXP '^(http|https)://'),
    FOREIGN KEY (id) REFERENCES Cuenta(id) ON DELETE CASCADE
);

-- Entidad Administrador
CREATE TABLE Administrador (
    id INT PRIMARY KEY,
    FOREIGN KEY (id) REFERENCES Cuenta(id) ON DELETE CASCADE
);

-- Entidad Categoría
CREATE TABLE Categoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT
);

-- Entidad Subcategoría
CREATE TABLE Subcategoria (
    id_categoria INT NOT NULL,
    id_subcategoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    historia TEXT,
    caracteristicas TEXT,
    requerimientos TEXT,
    tutoriales TEXT,
    FOREIGN KEY (id_categoria) REFERENCES Categoria(id) ON DELETE CASCADE
);

-- Entidad Etiqueta
CREATE TABLE Etiqueta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL UNIQUE,
    id_categoria INT NULL,
    id_subcategoria INT NULL,
    FOREIGN KEY (id_categoria) REFERENCES Categoria(id) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria, id_subcategoria) REFERENCES Subcategoria(id_categoria, id_subcategoria) ON DELETE CASCADE
);

-- Entidad Publicacion
CREATE TABLE Publicacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    urlContenido VARCHAR(2083) NOT NULL,
    descripcion TEXT,
    id_etiqueta INT,
    fecha_publicacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    likes INT DEFAULT 0,
    CHECK (urlContenido REGEXP '^(http|https)://'),
    FOREIGN KEY (id_etiqueta) REFERENCES Etiqueta(id) ON DELETE SET NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE
);

-- Entidad Comentario
CREATE TABLE Comentario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_publicacion INT NOT NULL,
    contenido TEXT NOT NULL,
    fecha_publicacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (id_publicacion) REFERENCES Publicacion(id) ON DELETE CASCADE
);


-- Relación de usuarios guardando publicaciones
CREATE TABLE Usuario_Guarda_Publicacion (
    id_usuario INT NOT NULL,
    id_publicacion INT NOT NULL,
    PRIMARY KEY (id_usuario, id_publicacion),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (id_publicacion) REFERENCES Publicacion(id) ON DELETE CASCADE
);

-- Relación de usuarios guardando categorías
CREATE TABLE Usuario_Guarda_Categoria (
    id_usuario INT NOT NULL,
    id_categoria INT NOT NULL,
    PRIMARY KEY (id_usuario, id_categoria),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES Categoria(id) ON DELETE CASCADE
);

-- Relación de usuarios guardando subcategorías
CREATE TABLE Usuario_Guarda_Subcategoria (
    id_usuario INT NOT NULL,
    id_categoria INT NOT NULL,
    id_subcategoria INT NOT NULL,
    PRIMARY KEY (id_usuario, id_categoria, id_subcategoria),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria, id_subcategoria) REFERENCES Subcategoria(id_categoria, id_subcategoria) ON DELETE CASCADE
);

-- Relación de usuarios dando like a publicaciones
CREATE TABLE Usuario_Da_Like (
    id_usuario INT NOT NULL,
    id_publicacion INT NOT NULL,
    PRIMARY KEY (id_usuario, id_publicacion),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (id_publicacion) REFERENCES Publicacion(id) ON DELETE CASCADE
);


DELIMITER //

-- Trigger para aumentar el conteo de likes cuando un usuario da like
CREATE TRIGGER before_insert_like
AFTER INSERT ON Usuario_Da_Like
FOR EACH ROW
BEGIN
    UPDATE Publicacion
    SET likes = likes + 1
    WHERE id = NEW.id_publicacion;
END;
//

-- Trigger para disminuir el conteo de likes cuando un usuario quita su like
CREATE TRIGGER before_delete_like
AFTER DELETE ON Usuario_Da_Like
FOR EACH ROW
BEGIN
    UPDATE Publicacion
    SET likes = likes - 1
    WHERE id = OLD.id_publicacion;
END;

-- Trigger para crear automáticamente una etiqueta cuando se inserta una nueva categoría
CREATE TRIGGER after_insert_categoria
AFTER INSERT ON Categoria
FOR EACH ROW
BEGIN
    INSERT INTO Etiqueta (nombre, id_categoria)
    VALUES (NEW.nombre, NEW.id);
END;
//

-- Trigger para crear automáticamente una etiqueta cuando se inserta una nueva subcategoría
CREATE TRIGGER after_insert_subcategoria
AFTER INSERT ON Subcategoria
FOR EACH ROW
BEGIN
    INSERT INTO Etiqueta (nombre, id_categoria, id_subcategoria)
    VALUES (NEW.nombre, NEW.id_categoria, NEW.id_subcategoria);
END;

DELIMITER ;