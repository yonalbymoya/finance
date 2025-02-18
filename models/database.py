import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../database.db")

DB_NAME = "database.db"


def get_connection():
    # return sqlite3.connect(DB_PATH)
    print("Conectandose a la base de datos", DB_PATH)
    return sqlite3.connect(DB_PATH)


def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS presupuestos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            fecha TEXT NOT NULL,
            subtotal REAL NOT NULL,
            iva REAL NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE
        );
        """
    )
    cursor.execute(
        """        
        CREATE TABLE IF NOT EXISTS presupuesto_detalles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            presupuesto_id INTEGER NOT NULL,
            etapa INTEGER NOT NULL,
            descripcion TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            descuento REAL NOT NULL,
            importe REAL NOT NULL,
            FOREIGN KEY (presupuesto_id) REFERENCES presupuestos(id) ON DELETE CASCADE
        );
    """
    )

    conn.commit()
    conn.close()


def add_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, password)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Usuario '{username}' ya existe.")
    conn.close()


def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    print("Esto es el usuario: ", user)
    conn.close()
    return user


def get_or_create_empresa(nombre):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM empresas WHERE nombre = ?", (nombre,))
    empresa = cursor.fetchone()
    if empresa:
        empresa_id = empresa[0]
    else:
        cursor.execute("INSERT INTO empresas (nombre) VALUES (?)", (nombre,))
        empresa_id = cursor.lastrowid
        conn.commit()
    conn.close()
    return empresa_id


def save_presupuesto(
    empresa_nombre, nombre_presupuesto, fecha, subtotal, iva, total, etapas
):
    conn = get_connection()
    cursor = conn.cursor()

    empresa_id = get_or_create_empresa(empresa_nombre)

    cursor.execute(
        """
        INSERT INTO presupuestos (empresa_id, nombre, fecha, subtotal, iva, total) 
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (empresa_id, nombre_presupuesto, fecha, subtotal, iva, total),
    )
    presupuesto_id = cursor.lastrowid

    for etapa in etapas:
        cursor.execute(
            """
        INSERT INTO presupuesto_detalles (presupuesto_id, etapa, descripcion, cantidad, precio, descuento, importe)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                presupuesto_id,
                etapa["etapa"],
                etapa["descripcion"],
                etapa["cantidad"],
                etapa["precio"],
                etapa["descuento"],
                etapa["importe"],
            ),
        )

    conn.commit()
    conn.close()
    return presupuesto_id


def get_presupuestos_by_empresa(empresa_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, nombre, fecha, subtotal, iva, total
        FROM presupuestos
        WHERE empresa_id = ?
    """,
        (empresa_id,),
    )
    presupuestos = cursor.fetchall()
    conn.close()
    return presupuestos


def get_presupuestos_by_id(presupuesto_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT p.id, p.nombre, p.fecha, p.subtotal, p.iva, p.total, e.nombre as empresa
        FROM presupuestos p
        JOIN empresas e ON p.empresa_id = e.id
        WHERE p.id = ?
        """,
        (presupuesto_id,),
    )
    presupuesto = cursor.fetchone()

    if not presupuesto:
        conn.close()
        return None

    cursor.execute(
        """
        SELECT etapa, descripcion, cantidad, precio, descuento, importe
        FROM presupuesto_detalles
        WHERE presupuesto_id = ?
        ORDER BY etapa ASC
        """
    )

    etapas = cursor.fetchall()

    conn.close()

    return {
        "id": presupuesto[0],
        "nombre": presupuesto[1],
        "fecha": presupuesto[2],
        "subtotal": presupuesto[3],
        "iva": presupuesto[4],
        "total": presupuesto[5],
        "empresa": presupuesto[6],
        "etapas": etapas,
    }


if __name__ == "__main__":
    create_tables()
    add_user("admin", "1234")  # Agregamos un usuario de prueba
