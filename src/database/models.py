import sqlite3
import pandas as pd

def get_db(): 
    return sqlite3.connect('estoque.db')

# --- FUNÇÕES QUE AS PÁGINAS ESTÃO PROCURANDO ---

def buscar_tudo():
    # Esta função é usada pelo Estoque.py
    # Ela calcula o estoque real e renomeia para 'quantidade' para não quebrar seus gráficos
    query = '''
        SELECT p.*, 
        COALESCE(SUM(CASE WHEN m.tipo = 'ENTRADA' THEN m.quantidade ELSE -m.quantidade END), 0) as quantidade
        FROM produtos p
        LEFT JOIN movimentacoes m ON p.id = m.id_produto
        GROUP BY p.id
    '''
    with get_db() as conn:
        df = pd.read_sql_query(query, conn)
        return df

def buscar_produtos_com_estoque():
    # Algumas páginas podem chamar esta função
    return buscar_tudo()

def salvar_produto_inteligente(nome, cod_barras, marca, espec, peso, categoria, validade, qtd, est_min, fornecedor, p_venda, p_custo, ncm, local, status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO produtos (nome, codigo_barras, marca, especificacao, peso, categoria, preco_venda, preco_custo, ncm, estoque_minimo, localizacao, status)
                      VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''', 
                   (nome, cod_barras, marca, espec, peso, categoria, p_venda, p_custo, ncm, est_min, local, status))
    id_produto = cursor.lastrowid
    if qtd > 0:
        cursor.execute('''INSERT INTO movimentacoes (id_produto, tipo, quantidade, preco_custo, validade, fornecedor)
                          VALUES (?, 'ENTRADA', ?, ?, ?, ?)''', (id_produto, qtd, p_custo, validade, fornecedor))
    conn.commit()
    conn.close()
    return True

def buscar_produtos_proximos_vencimento():
    with get_db() as conn: 
        return pd.read_sql_query("SELECT p.nome, p.id, m.validade FROM produtos p JOIN movimentacoes m ON p.id = m.id_produto WHERE m.validade IS NOT NULL", conn)

def reduzir_estoque(id_produto):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO movimentacoes (id_produto, tipo, quantidade) VALUES (?, 'SAIDA', 1)", (id_produto,))
    conn.commit()
    conn.close()

def excluir_produto(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def atualizar_produto(id, nome, cod_barras, marca, espec, peso, categoria, est_min, fornecedor, p_venda, p_custo, ncm):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''UPDATE produtos SET nome=?, codigo_barras=?, marca=?, especificacao=?, peso=?, categoria=?, estoque_minimo=?, fornecedor=?, preco_venda=?, preco_custo=?, ncm=? 
                      WHERE id=?''', (nome, cod_barras, marca, espec, peso, categoria, est_min, fornecedor, p_venda, p_custo, ncm, id))
    conn.commit()
    conn.close()