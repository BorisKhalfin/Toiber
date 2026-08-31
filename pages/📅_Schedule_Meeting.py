import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, time, timedelta
import json

# Page config
st.set_page_config(page_title="Lab Meeting Scheduler", page_icon="📅", layout="wide")

# SQLite init
DB_PATH = "data/meetings.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS polls (
            id TEXT PRIMARY KEY,
            title TEXT,
            dates TEXT,       -- JSON dates ['YYYY-MM-DD', ...]
            hours TEXT        -- JSON Hours ['09:00', '10:00', ...]
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            poll_id TEXT,
            user_name TEXT,
            availability TEXT, -- JSON matrix (0/1/2)
            PRIMARY KEY (poll_id, user_name)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Defining functions
def save_response(poll_id, user_name, matrix):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO responses (poll_id, user_name, availability)
        VALUES (?, ?, ?)
    ''', (poll_id, user_name, json.dumps(matrix)))
    conn.commit()
    conn.close()

def load_responses(poll_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT user_name, availability FROM responses WHERE poll_id = ?', (poll_id,))
    rows = c.fetchall()
    conn.close()
    return {row[0]: json.loads(row[1]) for row in rows}

# Frontend
st.title("📅 Lab Meeting Scheduler")
st.caption("Selecting the most suitable time for our meeting")

tab_vote, tab_results, tab_create = st.tabs([
    "✏️ Select my time", 
    "📊 General view", 
    "➕ New meeting"
])

# Example
DEMO_DATES = ["Mon (Sep 07)", "Tue (Sep 08)", "Wed (Sep 09)", "Thu (Sep 10)"]
DEMO_HOURS = [f"{h:02d}:00" for h in range(9, 18)]

# ==========================================
# Select yout time
# ==========================================
with tab_vote:
    st.subheader("Select your availability")
    
    col_user, col_status = st.columns([1, 2])
    with col_user:
        user_name = st.text_input("Your name:", placeholder="e.g. My majesty.")
    
    if user_name:
        st.markdown("**Instruction:** Select the slots you are **Available**.")
        
        # Load responces
        existing_responses = load_responses("lab_demo")
        init_matrix = existing_responses.get(user_name, np.zeros((len(DEMO_HOURS), len(DEMO_DATES))).tolist())
        
        # Table of all
        df_grid = pd.DataFrame(
            np.array(init_matrix) > 0,
            index=DEMO_HOURS,
            columns=DEMO_DATES
        )
        
        edited_df = st.data_editor(
            df_grid,
            column_config={
                col: st.column_config.CheckboxColumn(col, default=False)
                for col in DEMO_DATES
            },
            use_container_width=True,
            height=380
        )
        
        if st.button("💾 Save", type="primary"):
            save_matrix = edited_df.values.astype(int).tolist()
            save_response("lab_demo", user_name, save_matrix)
            st.toast(f"Ответы для {user_name} Saved!", icon="✅")
            st.rerun()

# ==========================================
# Heatmap
# ==========================================
with tab_results:
    st.subheader("Heatmap")
    
    responses = load_responses("lab_demo")
    
    if not responses:
        st.info("You are the first!")
    else:
        participants = list(responses.keys())
        matrices = [np.array(v) for v in responses.values()]
        total_matrix = sum(matrices)
        total_count = len(participants)
        
        col_summary, col_legend = st.columns([3, 1])
        
        with col_legend:
            st.markdown(f"**Reacted ({total_count}):**")
            for p in participants:
                st.markdown(f"- `{p}`")
        
        with col_summary:
            # Heatmap
            fig = px.imshow(
                total_matrix,
                x=DEMO_DATES,
                y=DEMO_HOURS,
                labels=dict(x="Day", y="Time", color="Available"),
                color_continuous_scale="Blues",
                text_auto=True
            )
            
            fig.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                margin=dict(l=10, r=10, t=30, b=10),
                height=420
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Golden Slots
        max_available = np.max(total_matrix)
        best_slots = np.argwhere(total_matrix == max_available)
        
        st.divider()
        if max_available == total_count:
            st.success(f"🎉 **Ideal option (Golden Slot):** everyone {total_count} available!")
        else:
            st.warning(f"⭐ **Best** Available **{max_available} из {total_count}** researchers:")
            
        cols_slots = st.columns(len(best_slots) if len(best_slots) <= 4 else 4)
        for idx, pos in enumerate(best_slots):
            r, c = pos[0], pos[1]
            with cols_slots[idx % 4]:
                st.info(f"📍 **{DEMO_DATES[c]}**\n\n⏰ **{DEMO_HOURS[r]}**")

# ==========================================
# New meeting
# ==========================================
with tab_create:
    st.subheader("New meeting")
    st.text_input("Name:", placeholder="e.g. SIRT6 Journal Club")
    st.date_input("Dates:", [])
    st.slider("Hours:", value=(9, 18), min_value=7, max_value=22)
    st.button("Create a linkс", disabled=True, help="Coming soon")
