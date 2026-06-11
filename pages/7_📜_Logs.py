import streamlit as st
from src.database.models import buscar_logs

st.header("📜 Histórico de Ações")
st.dataframe(buscar_logs(), use_container_width=True)