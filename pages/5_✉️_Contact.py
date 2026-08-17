import streamlit as st

st.set_page_config(page_title="Contact | Toiber Lab", page_icon="✉️", layout="wide")

st.title("✉️ Contact & Location")
st.write("Get in touch with us or find our laboratory.")

st.divider()

col_info, col_map = st.columns([1, 1])

with col_info:
    st.markdown("""
    **Principal Investigator:** Professor Debra Toiber  
    **Department:** Department of Life Sciences  
    **Faculty:** Faculty of Natural Sciences  
    **Institution:** Ben-Gurion University of the Negev  
    **Location:** Life Sciences Building (40) 
    **Debbie's office:** Room 205  
    **Laboratory** Rooms: 204, 206, 210, -147, -151  
    **Phone number:** (+972) 8 646 1371  
    **Email:** `toiber@bgu.ac.il`
    """)

with col_map:
    st.image("assets/Map.png" , caption="Our lab")
