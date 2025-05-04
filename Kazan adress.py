import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Распределение адресов по районам", layout="wide")
st.title("📊 Дашборд: адреса по районам")

@st.cache_data
def load_data():
    df_addr = pd.read_csv("data/addresses.csv", encoding="utf-8")
    df_dist = pd.read_csv("data/districts.csv", encoding="utf-8")

    df = df_addr.merge(df_dist, on="district_id", how="left")
    return df

df = load_data()

st.sidebar.markdown("## Фильтры")

stats = (
    df
    .groupby("district_name", as_index=False)
    .agg(count_addresses=pd.NamedAgg("address", "count"))
    .sort_values("count_addresses", ascending=False)
)

col1, col2 = st.columns((2,1))

with col1:
    fig = px.bar(
        stats,
        x="district_name",
        y="count_addresses",
        labels={
            "district_name": "Район",
            "count_addresses": "Число адресов"
        },
        title="Распределение адресов по районам",
        template="plotly_white"
    )
    fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.write("### Таблица с результатами")
    st.dataframe(stats, height=600)

git init
