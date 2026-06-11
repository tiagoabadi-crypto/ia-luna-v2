import streamlit as st
# IMPORTANTE: Use a nova função de cadastro
from src.database.models import cadastrar_produto_completo, atualizar_produto, excluir_produto, buscar_tudo

st.set_page_config(page_title="IA Luna - Gestão", layout="wide")
st.header("➕ Gestão de Produtos")

aba_cadastro, aba_edicao = st.tabs(["Novo Cadastro", "Editar/Excluir"])

with aba_cadastro:
    with st.form("cadastro", clear_on_submit=True):
        c1, c2 = st.columns(2)
        cod_barras = c1.text_input("Código de Barras")
        nome = c2.text_input("Nome do Produto")
        
        c3, c4, c5 = st.columns(3)
        marca = c3.text_input("Marca")
        peso = c4.number_input("Peso (g/ml)", 0.0, step=0.001, format="%g")
        categoria = c5.text_input("Categoria")
        
        espec = st.text_input("Especificação")
        
        c6, c7, c8 = st.columns(3)
        p_venda = c6.number_input("Preço de Venda (R$)", 0.0, format="%.2f")
        p_custo = c7.number_input("Preço de Custo (R$)", 0.0, format="%.2f")
        ncm = c8.text_input("NCM")
        
        c9, c10, c11 = st.columns(3)
        qtd_inicial = c9.number_input("Qtd Inicial", 0, step=1) # Usando a variável do novo modelo
        est_min = c10.number_input("Estoque Mínimo", 0, step=1)
        validade = c11.text_input("Validade (DD/MM/AAAA)")
        
        fornecedor = st.text_input("Fornecedor")
        
        local = st.selectbox("Localização na Loja (Nicho)", [
            "Nicho A: Frios e Laticínios", "Nicho B: Limpeza", "Nicho C: Bebidas", 
            "Nicho D: Mercearia", "Nicho E: Bolachas e Salgadinhos", 
            "Nicho F: Balas e Chocolates", "Nicho G: Outros"
        ])
        status = st.selectbox("Status", ["Ativo", "Inativo"])

        btn_submit = st.form_submit_button("Salvar Produto")

    if btn_submit:
        try:
            # Chama a função que salva o produto E registra a movimentação inicial
            cadastrar_produto_completo(nome, cod_barras, categoria, p_venda, p_custo, est_min, qtd_inicial, validade, fornecedor)
            st.success("Produto cadastrado com sucesso!")
            st.balloons()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

with aba_edicao:
    df = buscar_tudo()
    if not df.empty:
        produto_selecionado = st.selectbox("Escolha o produto para editar:", df['nome'].tolist())
        produto_info = df[df['nome'] == produto_selecionado].iloc[0]
        
        with st.form("form_edicao", clear_on_submit=False):
            st.subheader(f"Editando: {produto_info['nome']}")
            
            # Campos de edição (Removi a QTD aqui, pois não se edita estoque diretamente)
            c1, c2 = st.columns(2)
            cod_barras = c1.text_input("Código de Barras", value=produto_info['codigo_barras'])
            nome = c2.text_input("Nome do Produto", value=produto_info['nome'])
            
            c3, c4, c5 = st.columns(3)
            marca = c3.text_input("Marca", value=produto_info.get('marca', ''))
            peso = c4.number_input("Peso (g/ml)", value=float(produto_info.get('peso', 0)), step=0.001, format="%g")
            categoria = c5.text_input("Categoria", value=produto_info['categoria'])
            
            espec = st.text_input("Especificação", value=produto_info.get('especificacao', ''))
            
            c6, c7, c8 = st.columns(3)
            p_venda = c6.number_input("Preço de Venda (R$)", value=float(produto_info['preco_venda']), format="%.2f")
            p_custo = c7.number_input("Preço de Custo (R$)", value=float(produto_info['preco_custo']), format="%.2f")
            ncm = c8.text_input("NCM", value=produto_info.get('ncm', ''))
            
            est_min = st.number_input("Estoque Mínimo", value=int(produto_info['estoque_minimo']), step=1)
            fornecedor = st.text_input("Fornecedor", value=produto_info.get('fornecedor', ''))
            
            # Botões
            c_salvar, c_excluir = st.columns([4, 1])
            if c_salvar.form_submit_button("💾 Salvar Alterações"):
                # IMPORTANTE: Não enviamos QTD para atualizar_produto pois estoque é calculado
                atualizar_produto(
                    int(produto_info['id']), nome, cod_barras, marca, espec, peso, 
                    categoria, est_min, fornecedor, p_venda, p_custo, ncm
                )
                st.success("Produto atualizado!")
                st.rerun()
            
            if c_excluir.form_submit_button("🗑️ Excluir"):
                excluir_produto(int(produto_info['id']))
                st.warning("Produto excluído!")
                st.rerun()
    else:
        st.info("Nenhum produto cadastrado.")