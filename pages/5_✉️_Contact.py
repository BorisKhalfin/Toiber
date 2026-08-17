import streamlit as st

st.set_page_config(page_title="Contact | Toiber Lab", page_icon="✉️", layout="wide")

st.title("✉️ Contact & Location")
st.write("Get in touch with us or find our laboratory.")

st.divider()

col_info, col_map = st.columns([1, 1])

with col_info:
    st.markdown("""
    **Principal Investigator:** Dr. Debra Toiber  
    **Department:** Department of Life Sciences  
    **Institution:** Ben-Gurion University of the Negev  
    **Location:** Be'er Sheva, Israel  
    **Email:** `toiber@bgu.ac.il`
    """)

with col_map:
    st.info("📍 Map location and detailed directions will be rendered here.")
