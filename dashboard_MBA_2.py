import os
import json
import pandas as pd
import streamlit as st
from datetime import date
import plotly.express as px
from pathlib import PurePath


def get_color(category):
    try:
        if category == 'MUY ALTA VENTA' or category == 'ALTA VENTA':
            return '#27ae60'
        elif category == 'MEDIA VENTA':
            return '#f1c40f'
        elif category == 'BAJA VENTA':
            return '#e67e22'
        else:
            return "#c0392b"
    except:
        return "#c0392b"


@st.cache
def init():
    with open(PurePath(os.getcwd(), 'constants.json'), encoding='utf-8') as json_file:
        files = json.load(json_file)
    sales = pd.read_csv(
        PurePath(os.getcwd(), 'data', 'sales.csv'), encoding='utf-8')
    relations = pd.read_csv(
        PurePath(os.getcwd(), 'data', 'metrics.csv'), encoding='utf-8')
    stores = pd.read_csv(
        PurePath(os.getcwd(), 'data', 'tiendas.csv'), encoding='utf-8')
    return files, sales, relations, stores


@st.cache
def set_secund_table():
    df = relations.loc[(relations['prod_A'] == sku_ancla) & (
        relations['category_b'] == level_venta) & (relations['tipo'] == sku_asociado_tendencia), ['prod_B', 'estado', 'canal', 'gec', 'lift', 'sales_b', 'support_b', 'category_b','tendencia','tipo']]
    
    if type_order == 'TOP':
        tor = False
    else:
        tor = True

    df = df.sort_values(by='lift', ascending=tor)
    df = df.head(No_skus_top)
    df.rename({'prod_B': 'Producto (B)', 'sales_b': 'Venta (B)',
                         'lift': 'Lift', 'support_b': 'Support (B)'}, axis=1, inplace=True)
    df = df.reset_index(drop=True)
    return df

@st.cache
def set_options():
    return sales.loc[(sales['category'] == sku_segment) & (sales['tipo'] == sku_ancla_tendencia), 'product'].values


@st.cache
def validation_oportunity(value, x0, x1, y0, y1):
    if value['Lift'] >= x0 and value['Lift'] <= x1 and value['Venta (B)'] >= y0 and value['Venta (B)'] <= y1:
        return "Oportunidad de incremento en venta"
    else:
        return ""


def local_css():
    path = PurePath(os.getcwd(), 'style.css')
    with open(path) as f:
        st.markdown('<style>{}</style>'.format(f.read()),
                    unsafe_allow_html=True)

# ---------------------------------------------------------------------------- #
# ------------------------------- Configuración ------------------------------ #
# Page Config
st.set_page_config(page_title="Market Basket Analysis (MBA)",
                   initial_sidebar_state="expanded",
                   layout='wide',
                   page_icon="🛒")

constants_var, sales, relations, stores = init()
local_css()

# ---------------------------------------------------------------------------- #
# ------------------------------- Elementos Top ------------------------------ #
# Logo
row = st.columns(1)
row[0].header("🛒 Market Basket Analysis")
row[0].image("img/header_2.png", use_column_width=True)

st.markdown("***")
# # ---------------------------------------------------------------------------- #
# # --------------------------- Heatmap Combinaciones -------------------------- #

col8 = st.columns(1)
colt = st.columns(1)
col9 = st.columns(1)
col10 = st.columns(1)
colt2 = st.columns(1)
col11 = st.columns(1)
col12 = st.columns(1)

col8[0].header("Filtros de informacion")
col8[0].subheader("Filtros del SKU ancla")

with col8[0]:
    sku_segment = st.selectbox(
        label="Segmento SKU ancla", options=constants_var['segment'], index=0)
with colt[0]:
    sku_ancla_tendencia = st.selectbox(
        label="Tendencia SKU ancla", options=constants_var['tendencias'], index=0)
with col9[0]:
    sku_ancla = st.selectbox(label="SKU ancla",
                             options=set_options(), index=0)

col10[0].subheader("Filtros del SKU asociado")
with col10[0]:
    level_venta = st.selectbox(
        label="Nivel de venta SKU asociado", options=constants_var['segment'], index=0)
with colt2[0]:
    sku_asociado_tendencia = st.selectbox(
        label="Tendencia SKU asociado", options=constants_var['tendencias'], index=0)
with col11[0]:
    No_skus_top = st.number_input(
        min_value=5, max_value=25, value=10, step=5, label="Num SKUs (Top / Button)")
with col12[0]:
    type_order = st.selectbox(
        label="Top / Button Asociados", options=['TOP', 'BUTTON'], index=0)

st.markdown("***")

col13 = st.columns(1)
col13[0].header("Top {} de productos {} relacionados al producto ancla".format(
    No_skus_top, 'más' if type_order == 'TOP' else 'menos'))
data = set_secund_table()

with col13[0]:
    ndata = data[['Producto (B)', 'Venta (B)', 'Lift', 'Support (B)']].copy()
    st.dataframe(ndata, width=2000, height=2000)

st.markdown("***")
col14 = st.columns(1)
col14[0].header("Oportunidades de Impulso de Productos")

with col14[0]:
    impulso_venta = data.copy()
    x_0 = ((impulso_venta["Lift"].max(
    )-impulso_venta["Lift"].min())/2)+impulso_venta["Lift"].min()
    x_1 = round(impulso_venta["Lift"].max(), 1) + impulso_venta["Lift"].min()
    y_0 = 0
    y_1 = impulso_venta['Venta (B)'].max() * .5
    impulso_venta['category'] = impulso_venta.apply(
        lambda x: validation_oportunity(x, x_0, x_1, y_0, y_1), axis=1)

    plot3 = px.scatter(impulso_venta, x="Lift", y="Venta (B)",
                       color="category", size="Support (B)",
                       hover_data=[
                           'Producto (B)', 'category', 'Venta (B)', 'Support (B)'],
                       log_x=True
                       )
    plot3.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))
    plot3.add_shape(
        type="rect",
        x0=x_0,
        y0=y_0,
        x1=x_1,
        y1=y_1,
        line=dict(color="Crimson", width=2)
    )
    st.plotly_chart(
        plot3, config={'displayModeBar': False}, use_container_width=True)


st.markdown("***")
col15 = st.columns(1)
col15[0].header("Tendencias de los productos relacionados")

with col15[0]:
    ndata = data[['Producto (B)','tendencia', 'tipo']].copy()
    ndata['tendencia'] = ndata['tendencia'].apply(lambda x: json.loads(x))
    ndata =  ndata.explode('tendencia')
    ndata['Fecha'] = ['2018-10-01','2018-11-01','2018-12-01'] * len(ndata['Producto (B)'].unique())

    plot4 = px.line(ndata,x="Fecha", y="tendencia", color="Producto (B)",markers=True,
                        hover_data=['Producto (B)','Fecha' ,'tipo'],
                       log_x=True
                       )
    plot4.update_xaxes(type='category')
    st.plotly_chart(
        plot4, use_container_width=True)

