import os
import json
import pandas as pd
import streamlit as st
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

# @st.cache
def set_table():
    df = relations.loc[(relations['estado'] == region) & (
        relations['canal'] == channel) & (relations['gec'] == gec), ['prod_A', 'prod_B', 'lift']]
    df = sales.merge(df, left_on='product', right_on='prod_A', how='inner')
    df = df.sort_values(by='sales')

    skus = stores.loc[stores['tienda'] == tienda,['producto','cu','category']]
    skus = skus.sort_values(by='cu')


    values_order_1 = skus['producto'].unique() #[:n_sku]
    values_order_2 = values_order_1[::-1]

    values = []
    index = []
    colors = []
    count = 1

    for product in values_order_1:
        data = df.loc[df['product'] == product]
        data = data.sort_values(by='lift', ascending=False)
        data = data.drop_duplicates()
        data = data.head(n_top)
        sub_values = []
        for i in range(0, n_top):
            try:
                ndata = data.iloc[i]['prod_B']
                sub_values.append(ndata)
                try:
                    [category] = skus.loc[skus['producto'] == ndata,'category'].values
                    colors.append((count, 'No. {}'.format(str(i+1)), get_color(category)))
                except:
                    colors.append((count, 'No. {}'.format(str(i+1)), get_color("")))
            except:
                pass

        if len(sub_values) == n_top:
            index.append(product)
            values.append(sub_values)
            count += 1
            if len(index) == n_sku:
                break
        

    index = pd.Index(index, name="Top {}".format(n_top))
    df1 = pd.DataFrame(data=values, index=index, columns=[
                       'No. {}'.format(str(x)) for x in range(1, n_top+1)])
    
    def highlight(x):
        ndf1 = pd.DataFrame('', index=x.index, columns=x.columns)
        for c in colors:
            color = 'background-color: {}'.format(c[2])
            ndf1.at[c[0], c[1]] = color
        return ndf1

    df1 = df1.reset_index()
    df1.index += 1 

    df1 = df1.style.apply(lambda x: highlight(x), axis=None)

    values = []
    index = []
    colors_un = []
    count = 1

    for product in values_order_2:
        data = df.loc[df['product'] == product]
        data = data.sort_values(by='lift', ascending=False)
        data = data.drop_duplicates()
        data = data.head(n_top)
        sub_values = []
        for i in range(0, n_top):
            try:
                ndata = data.iloc[i]['prod_B']
                try:
                    [category] = skus.loc[skus['producto'] == ndata,'category'].values
                    colors_un.append((count, 'No. {}'.format(str(i+1)), get_color(category)))
                except:
                    colors_un.append((count, 'No. {}'.format(str(i+1)), get_color("")))
                sub_values.append(ndata)
            except:
                pass

        if len(sub_values) == n_top:
            index.append(product)
            values.append(sub_values)
            count += 1
            if len(index) == n_sku:
                break

    index = pd.Index(index, name="Buttom {}".format(n_top))
    df2 = pd.DataFrame(data=values, index=index, columns=[
                       'No. {}'.format(str(x)) for x in range(1, n_top+1)])
    df2 = df2.reset_index()
    df2.index += 1 

    def highlight_2(x):
        ndf2 = pd.DataFrame('', index=x.index, columns=x.columns)
        for c in colors_un:
            color = 'background-color: {}'.format(c[2])
            ndf2.at[c[0], c[1]] = color
        return ndf2

    df2 = df2.style.apply(lambda x: highlight_2(x), axis=None)
    return df1, df2, df[['product', 'category']]

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

# ---------------------------------------------------------------------------- #
# ----------------------------- Cargar Dataframe ----------------------------- #
col1 = st.columns(1)
col2 = st.columns(1)
col3 = st.columns(1)
col4 = st.columns(1)
col5 = st.columns(1)
col6 = st.columns(1)

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
with col6[0]:
    tienda = st.selectbox(
        label="Tienda", options=stores['tienda'].unique(), index=0)

st.markdown("***")

data_first, data_last, data_f = set_table()

# ---------------------------------------------------------------------------- #
# --------------------------- Table visualization ---------------------------- #
colheader = st.columns(1)
with colheader[0]:
    colheader[0].header("Productos sugeridos a recomendar al cliente")

st.markdown("***")

coltable1 = st.columns(1)
with coltable1[0]:
    st.subheader("Top {} de productos vendidos al cliente".format(str(n_top)))
    st.dataframe(data_first, height=2000)

coltable2 = st.columns(1)
with coltable2[0]:
    coltable2[0].subheader(
    "Bottom {} de productos vendidos al cliente".format(str(n_top)))
    st.dataframe(data_last, height=2000)

st.markdown("***")