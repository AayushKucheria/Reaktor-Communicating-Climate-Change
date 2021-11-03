import streamlit as st

st.write("The Climate Crisis. Tick Tock.")
# Create a sidebar with 3 pages
st.sidebar.header("Menu")
page = st.sidebar.radio("Pages", ("Home", "About", "Contact"))

