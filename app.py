import streamlit as st
from src.utils import saluta

st.title("🧮 Mini App di Esempio")
name = st.text_input("Come ti chiami?")
if name:
    st.success(saluta(name))

