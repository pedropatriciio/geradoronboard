import psycopg2
import os

# O Render vai fornecer essa variável
DATABASE_URL = os.environ.get("DATABASE_URL_TEST")



def get_connection():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL não configurada nas variáveis de ambiente")
    return psycopg2.connect(DATABASE_URL)


def init_db():
    # Nada a fazer aqui: no Supabase a tabela já foi criada manualmente
    pass


def buscar_colaborador(nome, papel):
    if not nome:
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