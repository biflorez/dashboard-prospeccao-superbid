
# dashboard_prospeccao.py
import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Carregar dados
@st.cache_data
def load_data():
    return pd.read_excel("Prospecção_Unificada_Superbid.xlsx", engine="openpyxl")

df = load_data()

st.set_page_config(page_title="Prospecção Comercial Superbid", layout="wide")
st.title("📊 Dashboard de Prospecção Comercial - Superbid")

# Filtros
setores = st.multiselect("Filtrar por Setor Industrial:", options=sorted(df["Setor"].dropna().unique()), default=None)
status = st.multiselect("Filtrar por Status:", options=sorted(df["Status"].dropna().unique()), default=None)

filtro = df.copy()
if setores:
    filtro = filtro[filtro["Setor"].isin(setores)]
if status:
    filtro = filtro[filtro["Status"].isin(status)]

# Métricas
st.metric("Total de Empresas", len(filtro))

# Gráficos
col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(filtro.groupby("Setor")["Empresa"].count().reset_index(),
                  x="Setor", y="Empresa", title="Empresas por Setor", labels={"Empresa": "Qtd. Empresas"})
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.pie(filtro, names="Status", title="Distribuição por Status")
    st.plotly_chart(fig2, use_container_width=True)

# Tabela detalhada
st.subheader("📋 Tabela de Empresas")

if "Receita Estimada (R$)" in filtro.columns:
    filtro["Receita Estimada (R$)"] = pd.to_numeric(filtro["Receita Estimada (R$)"], errors="coerce")
    filtro["Receita 2024"] = filtro["Receita Estimada (R$)"].apply(
        lambda x: f"R$ {x:,.0f}".replace(",", ".") if pd.notnull(x) else "N/A"
    )
    filtro_ordenado = filtro.sort_values(by="Receita Estimada (R$)", ascending=False, na_position="last")
    filtro_exibido = filtro_ordenado[["Empresa", "Setor", "Status", "Receita 2024"]]
    st.dataframe(filtro_exibido, use_container_width=True)
else:
    filtro_exibido = filtro
    st.dataframe(filtro, use_container_width=True)

# Exportar dados filtrados
output = io.BytesIO()
filtro_exibido.to_excel(output, index=False, engine="openpyxl")
st.download_button("📥 Baixar dados filtrados", data=output.getvalue(), file_name="Prospecao_Filtrada.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
