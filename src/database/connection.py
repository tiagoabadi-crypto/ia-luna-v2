import sqlite3

# Define o nome do banco de dados
DB_PATH = "estoque.db"

def get_connection():
    """Gerencia a conexão com o banco de dados de forma centralizada."""
    conn = sqlite3.connect(DB_PATH)
    # Ativa chaves estrangeiras (essencial para integridade do estoque)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn