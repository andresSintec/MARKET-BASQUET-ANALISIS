from PIL import Image
import streamlit as st
from templates import generate_sidebar

with st.sidebar:
    image = Image.open('./img/logo.png')
    st.image(image)
    st.markdown("<h1 id='title'>Portafolio de soluciones</h1>",
                unsafe_allow_html=True)
    st.markdown(generate_sidebar(), unsafe_allow_html=True)
    path = st.experimental_get_query_params()
    print(path)