import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS colaboradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            papel TEXT NOT NULL,
            email TEXT,
            telefone TEXT
        )
    """)

    conn.commit()
    conn.close()


def buscar_colaborador(nome, papel):
    if not nome:
        return None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT nome, email, telefone
        FROM colaboradores
        WHERE LOWER(nome) = LOWER(?)
          AND LOWER(papel) = LOWER(?)
        """,
        (nome.strip(), papel.strip())
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "nome": row[0],
        "email": row[1],
        "telefone": row[2],
    }


def listar_colaboradores():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT nome, papel, email, telefone FROM colaboradores"
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "nome": r[0],
            "papel": r[1],
            "email": r[2],
            "telefone": r[3],
        }
        for r in rows
    ]