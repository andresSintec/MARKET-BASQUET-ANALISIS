import os
import json
import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import PurePath


# @st.cache


def init():
    with open(PurePath(os.getcwd(), 'constants.json'), encoding='utf-8') as json_file:
        files = json.load(json_file)
    sales = pd.read_csv(
        PurePath(os.getcwd(), 'data', 'sales.csv'), encoding='utf-8')
    relations = pd.read_csv(
        PurePath(os.getcwd(), 'data', 'metrics.csv'), encoding='utf-8')
    return files, sales, relations

# @st.cache


def set_table():
    df = relations.loc[(relations['estado'] == region) & (
        relations['canal'] == channel) & (relations['gec'] == gec), ['prod_A', 'prod_B', 'lift']]
    df = sales.merge(df, left_on='product', right_on='prod_A', how='inner')
    df = df.sort_values(by='sales')

    values_order_1 = df['product'].unique()[:n_sku]
    values_order_2 = df['product'].unique()[n_sku * -1:]

    values = []
    index = []
    for product in values_order_1:
        data = df.loc[df['product'] == product]
        data = data.sort_values(by='lift', ascending=False)
        data = data.drop_duplicates()
        data = data.head(n_top)
        index.append(product)
        sub_values = []
        for i in range(0, n_top):
            ndata = data.iloc[i]
            sub_values.append(ndata['prod_B'])
        values.append(sub_values)

    index = pd.Index(index, name="SKU ancla")
    df1 = pd.DataFrame(data=values, index=index, columns=[
                       'No. {}'.format(str(x)) for x in range(1, n_top+1)])
    df1 = df1.reset_index()

    values = []
    index = []
    for product in values_order_2:
        data = df.loc[df['product'] == product]
        data = data.sort_values(by='lift', ascending=False)
        data = data.drop_duplicates()
        data = data.head(n_top)
        index.append(product)
        sub_values = []
        for i in range(0, n_top):
            ndata = data.iloc[i]
            sub_values.append(ndata['prod_B'])
        values.append(sub_values)
    
    index = pd.Index(index, name="SKU ancla")
    df2 = pd.DataFrame(data=values, index=index, columns=[
                       'No. {}'.format(str(x)) for x in range(1, n_top+1)])
    df2 = df2.reset_index()

    return df1, df2, df[['product', 'category']]

# @st.cache


def set_secund_table():
    df = relations.loc[(relations['prod_A'] == sku_ancla) & (
        relations['category_b'] == level_venta), ['prod_B', 'estado', 'canal', 'gec', 'lift', 'sales_b', 'support_b', 'category_b']]
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

# @st.cache


def set_options():
    return sales.loc[sales['category'] == sku_segment, 'product'].values

# @st.cache


def validation_oportunity(value, x0, x1, y0, y1):
    if value['Lift'] >= x0 and value['Lift'] <= x1 and value['Venta (B)'] >= y0 and value['Venta (B)'] <= y1:
        return "Alta probabilidad"
    else:
        return "Baja probabilidad"

def local_css():
    curdir = os.path.dirname(os.path.realpath(__file__)) + r'\\'
    css_file = os.path.join(curdir, 'style.css')
    with open(css_file) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)


# ---------------------------------------------------------------------------- #
# ------------------------------- Configuración ------------------------------ #
# Page Config
st.set_page_config(page_title="Market Basket Analysis (MBA)",
                   initial_sidebar_state="expanded",
                   layout='wide',
                   page_icon="🛒")

constants_var, sales, relations = init()
local_css()

# ---------------------------------------------------------------------------- #
# ------------------------------- Elementos Top ------------------------------ #
# Logo
row = st.columns(1)
row[0].header("🛒 Market Basket Analysis")
row[0].image("img/header_2.png", use_column_width=True)
st.markdown("***")

# ---------------------------------------------------------------------------- #
# ----------------------------- Cargar Dataframe ----------------------------- #
col1 = st.columns(1)
col2 = st.columns(1)
col3 = st.columns(1)
col4 = st.columns(1)
col5 = st.columns(1)

col1[0].header("Filtros de informacion")

with col1[0]:
    n_sku = st.number_input(min_value=5, max_value=25,
                            value=10, step=5, label="No. SKU's (Venta actual)")
with col2[0]:
    channel = st.selectbox(label="Canal de venta",
                           options=constants_var['channel'], index=0)
with col3[0]:
    gec = st.selectbox(
        label="Clasificación de cliente (GEC)", options=constants_var['gec'], index=0)
with col4[0]:
    region = st.selectbox(
        label="Estado / Region geografica", options=constants_var['state'], index=0)
with col5[0]:
    n_top = st.number_input(min_value=5, max_value=20,
                            value=10, step=5, label="Ranking SKU's (Top / Buttom)")

st.markdown("***")

data_first, data_last, data_f = set_table()

# ---------------------------------------------------------------------------- #
# --------------------------- Table visualization ---------------------------- #
col6 = st.columns(1)
col6[0].header(
    "Top {} de productos a recomendar al cliente".format(str(n_top)))


with col6[0]:
    st.dataframe(data_first, height=2000)

col7 = st.columns(1)
col7[0].header(
    "Top {} de productos con menor probabilidad de venta".format(str(n_top)))

with col7[0]:
    st.dataframe(data_last, height=2000)

st.markdown("***")

# # ---------------------------------------------------------------------------- #
# # --------------------------- Heatmap Combinaciones -------------------------- #

col8 = st.columns(1)
col9 = st.columns(1)
col10 = st.columns(1)
col11 = st.columns(1)
col12 = st.columns(1)

col8[0].header("Filtros de informacion")

with col8[0]:
    sku_segment = st.selectbox(
        label="Segmento SKU ancla", options=constants_var['segment'], index=0)
with col9[0]:
    sku_ancla = st.selectbox(label="SKU ancla",
                             options=set_options(), index=0)
with col10[0]:
    level_venta = st.selectbox(
        label="Nivel de venta SKU asociado", options=constants_var['segment'], index=0)
with col11[0]:
    No_skus_top = st.number_input(
        min_value=5, max_value=25, value=10, step=5, label="Num SKUs (Top / Button)")
with col12[0]:
    type_order = st.selectbox(
        label="Top / Button Asociados", options=['TOP', 'BUTTON'], index=0)

st.markdown("***")

col13 = st.columns(2)
col13[0].header("Top {} de productos {} relacionados al producto ancla".format(
    No_skus_top, 'Mas' if type_order == 'TOP' else 'Menos'))
data = set_secund_table()

with col13[0]:

    ndata = data[['Producto (B)', 'Venta (B)', 'Lift', 'Support (B)']].copy()
    st.dataframe(ndata, width=2000, height=2000)

st.markdown("***")

col13[1].header("Oportunidades de Impulso de Productos")

with col13[1]:
    impulso_venta = data.copy()

    x_0 = ((impulso_venta["Lift"].max(
    )-impulso_venta["Lift"].min())/2)+impulso_venta["Lift"].min()
    x_1 = round(impulso_venta["Lift"].max(), 1) + impulso_venta["Lift"].min()
    y_0 = 0
    y_1 = impulso_venta['Venta (B)'].max() * .5

    impulso_venta['category'] = impulso_venta.apply(
        lambda x: validation_oportunity(x, x_0, x_1, y_0, y_1), axis=1)

    plot3 = px.scatter(impulso_venta, x="Lift", y="Venta (B)",
                       color="category", size="Support (B)", text="Producto (B)", log_x=True)

    plot3.update_traces(textposition='top left')

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
