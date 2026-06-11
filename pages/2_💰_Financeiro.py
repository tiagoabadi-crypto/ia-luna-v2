import streamlit as st
import pandas as pd
import plotly.express as px
from src.database.models import buscar_tudo
from src.database.models import buscar_dados_financeiros

st.set_page_config(page_title="IA Luna - Financeiro", layout="wide")
st.header("💰 Visão Financeira (Modo Profissional)")

df = buscar_dados_financeiros()

if not df.empty and df['quantidade'].sum() > 0:
    # KPIs
    total_investido = df['valor_investido'].sum()
    total_venda = df['valor_venda'].sum()
    lucro_total = df['lucro_potencial'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Investimento", f"R$ {total_investido:,.2f}")
    c2.metric("📈 Valor de Venda", f"R$ {total_venda:,.2f}")
    c3.metric("💵 Lucro Esperado", f"R$ {lucro_total:,.2f}")

    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(df, x='nome', y='lucro_potencial', title="Lucro por Produto")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig_pie = px.pie(df, values='valor_investido', names='categoria', title="Capital Alocado por Categoria")
        st.plotly_chart(fig_pie, use_container_width=True)

    # Tabela
    st.dataframe(df, use_container_width=True)

else:
    st.info("Nenhuma movimentação registrada. O financeiro precisa de compras ou vendas.")

df = buscar_tudo()

if not df.empty:
    # 1. Cálculos base
    df['valor_investido'] = df['preco_custo'] * df['quantidade']
    df['valor_venda'] = df['preco_venda'] * df['quantidade']
    df['lucro_potencial'] = df['valor_venda'] - df['valor_investido']
    df['margem_%'] = (df['lucro_potencial'] / df['valor_venda']) * 100

    # 2. KPIs (Indicadores)
    total_investido = df['valor_investido'].sum()
    total_venda = df['valor_venda'].sum()
    lucro_total = df['lucro_potencial'].sum()
    margem_media = (lucro_total / total_venda) * 100 if total_venda > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Investimento Total", f"R$ {total_investido:,.2f}")
    c2.metric("📈 Valor de Venda", f"R$ {total_venda:,.2f}")
    c3.metric("💵 Lucro Esperado", f"R$ {lucro_total:,.2f}", delta=f"{margem_media:.1f}% Margem")
    c4.metric("📦 Produtos", len(df))

    # 3. Gráficos
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de Lucro por Produto
        fig_lucro = px.bar(df.sort_values('lucro_potencial', ascending=False).head(10), 
                           x='nome', y='lucro_potencial', title="Top 10 Produtos (Lucro Potencial)",
                           color='lucro_potencial', color_continuous_scale='Greens')
        st.plotly_chart(fig_lucro, use_container_width=True)
        
    with col2:
        # Gráfico de Distribuição do Lucro
        fig_dist = px.pie(df, values='lucro_potencial', names='categoria', title="Lucro por Categoria")
        st.plotly_chart(fig_dist, use_container_width=True)

    # 4. Tabela de Detalhe Financeiro
    st.subheader("Detalhamento por Produto")
    df_exibicao = df[['nome', 'quantidade', 'preco_custo', 'preco_venda', 'lucro_potencial', 'margem_%']]
    st.dataframe(df_exibicao, use_container_width=True, column_config={
        "preco_custo": st.column_config.NumberColumn("Custo", format="R$ %.2f"),
        "preco_venda": st.column_config.NumberColumn("Venda", format="R$ %.2f"),
        "lucro_potencial": st.column_config.NumberColumn("Lucro R$", format="R$ %.2f"),
        "margem_%": st.column_config.ProgressColumn("Margem %", format="%.1f%%", min_value=0, max_value=100)
    })

else:
    st.info("Estoque vazio. Adicione produtos para ver o financeiro.")