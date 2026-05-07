import os
import psycopg2

# ======================================================
# CONEXÃO COM O BANCO (SUPABASE / POSTGRES)
# ======================================================

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    """
    Cria uma nova conexão com o banco PostgreSQL do Supabase.
    """
    if not DATABASE_URL:
        raise Exception("DATABASE_URL não configurada nas variáveis de ambiente")

    return psycopg2.connect(DATABASE_URL)


def init_db():
    """
    Mantido apenas por compatibilidade.
    No Supabase a tabela já é criada manualmente.
    """
    pass


# ======================================================
# BUSCAR UM COLABORADOR (COMERCIAL OU CS)
# ======================================================

def buscar_colaborador(nome, papel):
    if not nome or not papel:
        return None

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT nome, email, telefone
        FROM colaboradores
        WHERE LOWER(nome) = LOWER(%s)
          AND LOWER(papel) = LOWER(%s)
        """,
        (nome.strip(), papel.strip())
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return None

    return {
        "nome": row[0],
        "email": row[1],
        "telefone": row[2],
    }


# ======================================================
# LISTAR TODOS OS COLABORADORES
# ======================================================

def listar_colaboradores():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT nome, papel, email, telefone
        FROM colaboradores
        ORDER BY nome
        """
    )

    rows = cur.fetchall()

    cur.close()
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