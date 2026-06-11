import streamlit as st
from src.database.models import init_db

init_db()

# 1. Configuração da página (deve ser a primeira coisa no script)
st.set_page_config(page_title="IA Luna - ERP", layout="wide")

# 2. Garantir que as tabelas existem no banco
init_db()

# 3. Aplicar estilo global (carregando do arquivo CSS que criamos)
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Garante que o arquivo de estilo existe antes de carregar
try:
    local_css("assets/style.css")
except:
    st.warning("Arquivo de estilo não encontrado. Crie a pasta 'assets' e o arquivo 'style.css'.")

# 4. Interface do Dashboard (Página Inicial)
st.title("🔐 IA Luna - Sistema de Gestão")
st.write("Bem-vindo ao sistema de gestão inteligente.")

# Autenticação Simples
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    senha = st.text_input("Digite a senha de acesso:", type="password")
    if st.button("Entrar"):
        if senha == "1234":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop() # Bloqueia o carregamento do restante se não estiver logado

# Se estiver autenticado:
st.success("Acesso autorizado! Use o menu lateral para navegar.")
st.markdown("---")
st.metric("Sistema", "Online", "v2.0")