import streamlit as st

st.set_page_config(
    page_title="Toiber Lab | Home",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header Section
st.title("Welcome to Toiber Lab 🧬")
st.subheader("Unraveling the Molecular Mechanisms of Longevity and Neurodegeneration")
st.caption("Department of Life Sciences | Ben-Gurion University of the Negev")

st.divider()

# Intro / Welcome block
col_about, col_img = st.columns([2, 1])

with col_about:
    st.markdown("""
    ### About Our Lab
    At the **Toiber Lab**, we investigate aging across biological scales. 
    We bridge the gap between microscopic molecular events and organismal health, 
    using **SIRT6** as our primary model to drive discoveries from the laboratory bench to therapeutic intervention.
    """)
    st.info("💡 Use the sidebar navigation on the left to explore our Team, Gallery, Publications, Events, and Extras!")

with col_img:
    st.image("https://placehold.co/400x300/003366/FFFFFF?text=Toiber+Lab+Logo", caption="Toiber Lab @ BGU")

st.divider()

# Quick Cards Navigation
st.markdown("### 🚀 Quick Navigation")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("#### 👥 Team")
    st.write("Meet our researchers, students, and lab members.")
with c2:
    st.markdown("#### 🖼️ Gallery")
    st.write("Lab life, food gatherings, and celebrations.")
with c3:
    st.markdown("#### 📚 Publications")
    st.write("Explore our peer-reviewed research articles.")
with c4:
    st.markdown("#### 🎙️ Podcast")
    st.write("Listen to discussions on aging and science.")
