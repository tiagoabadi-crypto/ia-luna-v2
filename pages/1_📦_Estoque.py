import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta
from src.database.models import buscar_produtos_com_estoque, buscar_produtos_proximos_vencimento, registrar_ajuste, reduzir_estoque
from src.database.models import buscar_tudo, buscar_produtos_proximos_vencimento, reduzir_estoque

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="IA Luna - Estoque", layout="wide")
st.header("📦 Gestão de Estoque")

df_raw = buscar_produtos_com_estoque()
df = df_raw.rename(columns={'quantidade_atual': 'quantidade'})

if not df.empty:

   hoje = datetime.now()
   prazo_limite = hoje + timedelta(days=15)

df = buscar_tudo()

if not df.empty:
    # --- 1. INDICADORES (KPIs) ---
    hoje = datetime.now()
    prazo_limite = hoje + timedelta(days=15)
    
    # Cálculo para KPIs
    total_produtos = len(df)
    total_qtd = df['quantidade'].sum()
    criticos = len(df[df['quantidade'] <= 5])
    
    # KPIs na tela
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Total de Produtos", total_produtos)
    c2.metric("🔢 Volume em Estoque", total_qtd)
    c3.metric("⚠️ Estoque Crítico", criticos, delta_color="inverse")

    # --- 2. AÇÕES E DOWNLOADS ---
    with st.expander("📥 Exportar e Backup"):
        c1, c2 = st.columns(2)
        csv = df.to_csv(index=False).encode('utf-8')
        c1.download_button("📥 Exportar CSV", data=csv, file_name='estoque.csv', mime='text/csv')
        
        if os.path.exists('estoque.db'):
            with open('estoque.db', 'rb') as f:
                c2.download_button("💾 Backup DB", data=f, file_name='estoque.db', mime='application/octet-stream')

    # --- 3. GRÁFICOS ---
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(df, x='nome', y='quantidade', title="Volume de Estoque", color='quantidade', color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            df['valor_total'] = df['preco_venda'] * df['quantidade']
            fig_valor = px.pie(df, values='valor_total', names='nome', title="Distribuição de Valor")
            st.plotly_chart(fig_valor, use_container_width=True)

    # --- 4. ALERTA DE VENCIMENTOS E CRÍTICOS ---
    st.divider()
    st.subheader("🚨 Avisos e Ações")
    
    tab1, tab2 = st.tabs(["⚠️ Vencimentos (15 dias)", "📉 Estoque Crítico"])
    
    with tab1:
        df_vencidos = buscar_produtos_proximos_vencimento()
        exibir_alerta = False
        
        for index, row in df_vencidos.iterrows():
            try:
                data_val = datetime.strptime(row['validade'], "%d/%m/%Y")
            except: continue

            if data_val <= prazo_limite:
                exibir_alerta = True
                status_venc = "VENCIDO" if data_val <= hoje else "Próximo ao vencimento"
                color = "red" if data_val <= hoje else "orange"
                
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    col1.markdown(f"**{row['nome']}** | <span style='color:{color}'>{status_venc}</span>", unsafe_allow_html=True)
                    col2.write(f"Data: {row['validade']}")
                    
                    if col3.button("📉 Baixa", key=f"baixa_{row['id']}"):
                        reduzir_estoque(row['id'])
                        st.rerun()
        if not exibir_alerta: st.success("Tudo em dia com as validades!")

    with tab2:
        baixo_estoque = df[df['quantidade'] <= 5]
        if not baixo_estoque.empty:
            st.dataframe(baixo_estoque[['nome', 'quantidade', 'fornecedor']], use_container_width=True, hide_index=True)
        else:
            st.success("Nenhum produto em nível crítico.")

    # --- 5. LISTA GERAL (INTELIGENTE) ---
    st.divider()
    st.subheader("📋 Lista Geral de Produtos")
    st.dataframe(
        df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "quantidade": st.column_config.ProgressColumn(
                "Qtd", format="%d", min_value=0, max_value=max(df['quantidade']) if not df.empty else 50
            ),
            "preco_venda": st.column_config.NumberColumn("Venda", format="R$ %.2f"),
            "preco_custo": st.column_config.NumberColumn("Custo", format="R$ %.2f"),
        }
    )

else:
    st.info("Estoque vazio no momento.")