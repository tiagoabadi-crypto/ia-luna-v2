import streamlit as st
from src.database.models import buscar_tudo, registrar_venda

st.header("🛒 Registrar Venda")
df = buscar_tudo()
if not df.empty:
    prod_id = st.selectbox("Selecione o produto:", df['id'].tolist(), 
                           format_func=lambda x: df[df['id']==x]['nome'].values[0])
    qtd_venda = st.number_input("Qtd vendida:", 1, step=1)
    if st.button("Confirmar Venda"):
        if registrar_venda(prod_id, qtd_venda):
            st.toast("Venda registrada!", icon="💰")
            st.rerun()