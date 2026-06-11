import streamlit as st
from src.database.models import buscar_tudo, adicionar_estoque, atualizar_produto, registrar_nova_compra

st.set_page_config(page_title="IA Luna - Compras", layout="wide")
st.header("🛒 Registrar Nova Compra / Reposição")

df = buscar_tudo()

if not df.empty:
    produto_selecionado = st.selectbox("Selecione o Produto para repor:", df['nome'].tolist())
    
    # Filtra os dados do produto selecionado para preencher os campos
    produto = df[df['nome'] == produto_selecionado].iloc[0]
    
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        
        # Inputs para o novo lote
        nova_qtd = col1.number_input("Quantidade comprada (adicionar ao estoque)", min_value=1, value=1)
        novo_custo = col2.number_input("Novo Preço de Custo (R$)", min_value=0.0, value=float(produto['preco_custo']))
        novo_venda = col3.number_input("Novo Preço de Venda (R$)", min_value=0.0, value=float(produto['preco_venda']))
        
        col4, col5 = st.columns(2)
        nova_validade = col4.text_input("Nova Validade (dd/mm/aaaa)", value=str(produto['validade']))
        novo_fornecedor = col5.text_input("Fornecedor", value=str(produto['fornecedor']))

        if st.button("Confirmar Compra / Reposição"):
            # 1. SEGURANÇA: Adiciona apenas a quantidade no banco
            adicionar_estoque(produto['id'], nova_qtd)
            
            # 2. ATUALIZAÇÃO: Atualiza os dados do produto (preços, fornecedor, validade)
            # Mantemos produto['quantidade'] pois o adicionar_estoque já cuidou de somar
            atualizar_produto(
                produto['id'], 
                produto['nome'], 
                produto['codigo_barras'], 
                produto['marca'], 
                produto['especificacao'], 
                produto['peso'], 
                produto['categoria'], 
                nova_validade, 
                produto['quantidade'], # Não somamos aqui, o banco já somou no passo anterior
                produto['estoque_minimo'], 
                novo_fornecedor, 
                novo_venda, 
                novo_custo, 
                produto['ncm'], 
                produto['localizacao'], 
                produto['status']
            )
            
            # 3. HISTÓRICO: Registra que uma compra ocorreu
            registrar_nova_compra(produto['id'], nova_qtd, novo_custo)
            
            st.success(f"Estoque de {produto_selecionado} atualizado! Novo custo: R$ {novo_custo:.2f}")
            st.balloons()
            st.rerun() 

    st.divider()
    st.info("💡 **Dica:** Ao alterar o preço de custo e venda aqui, o sistema atualizará o registro principal do produto, refletindo o custo do seu lote mais recente.")

else:
    st.warning("Nenhum produto encontrado. Cadastre produtos primeiro.")