import json
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Lab Meeting Scheduler", page_icon="📅", layout="wide")

# --- GOOGLE SHEETS AUTHENTICATION & CONNECTION ---
SPREADSHEET_URL = (
    "https://docs.google.com/spreadsheets/d/1qc_35xuLtks34Pn1_DmBW43V3Tex-_d3w__1yQivAzY/edit?usp=sharing"
)

@st.cache_resource
def get_gsheet_client():
    """Initializes the gspread client using Streamlit secrets or service account."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    
    # Check if Google credentials exist in st.secrets
    if "gcp_service_account" in st.secrets:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes
        )
        return gspread.authorize(creds)
    elif "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        creds = Credentials.from_service_account_info(
            st.secrets["connections"]["gsheets"], scopes=scopes
        )
        return gspread.authorize(creds)
    else:
        # Anonymous fallback for public sheets (read-only / limited access)
        return gspread.public_authorize()


def get_worksheet(sheet_name="responses"):
    """Fetches a specific worksheet from the spreadsheet."""
    client = get_gsheet_client()
    sheet = client.open_by_url(SPREADSHEET_URL)
    try:
        return sheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        # Create worksheet if it doesn't exist yet
        ws = sheet.add_worksheet(title=sheet_name, rows=100, cols=10)
        ws.append_row(["poll_id", "user_name", "availability", "updated_at"])
        return ws


def load_responses(poll_id="lab_demo"):
    """Fetches all responses for a given poll_id from Google Sheets."""
    try:
        ws = get_worksheet("responses")
        records = ws.get_all_records()
        if not records:
            return {}

        df = pd.DataFrame(records)
        if df.empty or "poll_id" not in df.columns:
            return {}

        poll_df = df[df["poll_id"] == poll_id]

        responses = {}
        for _, row in poll_df.iterrows():
            responses[row["user_name"]] = json.loads(str(row["availability"]))
        return responses
    except Exception as e:
        st.warning(f"Could not load data: {e}")
        return {}


def save_response(poll_id, user_name, matrix):
    """Saves or updates a participant's availability matrix in Google Sheets."""
    ws = get_worksheet("responses")
    records = ws.get_all_records()
    
    matrix_json = json.dumps(matrix)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    df = pd.DataFrame(records) if records else pd.DataFrame(columns=["poll_id", "user_name", "availability", "updated_at"])

    # Check for an existing record by the same participant
    if not df.empty and "poll_id" in df.columns and "user_name" in df.columns:
        mask = (df["poll_id"] == poll_id) & (df["user_name"] == user_name)
    else:
        mask = pd.Series([False])

    if mask.any():
        df.loc[mask, "availability"] = matrix_json
        df.loc[mask, "updated_at"] = now_str
    else:
        new_row = pd.DataFrame(
            [
                {
                    "poll_id": poll_id,
                    "user_name": user_name,
                    "availability": matrix_json,
                    "updated_at": now_str,
                }
            ]
        )
        df = pd.concat([df, new_row], ignore_index=True)

    # Overwrite worksheet with updated content
    ws.clear()
    ws.update([df.columns.values.tolist()] + df.values.tolist())


# --- UI LAYOUT ---
st.title("📅 Lab Meeting Scheduler")
st.caption("Find optimal meeting slots for lab seminars and discussions")

tab_vote, tab_results = st.tabs(["✏️ Select Availability", "📊 Team Results"])

DEMO_DATES = ["Mon (Sep 07)", "Tue (Sep 08)", "Wed (Sep 09)", "Thu (Sep 10)"]
DEMO_HOURS = [f"{h:02d}:00" for h in range(9, 18)]

# ==========================================
# TAB 1: Select Availability
# ==========================================
with tab_vote:
    st.subheader("Mark Your Availability")

    col_user, _ = st.columns([1, 2])
    with col_user:
        user_name = st.text_input("Your Name / Initials:", placeholder="e.g. Boris K.")

    if user_name:
        st.markdown("**Instructions:** Check the boxes for times when you are **available**.")

        existing_responses = load_responses("lab_demo")
        init_matrix = existing_responses.get(
            user_name, np.zeros((len(DEMO_HOURS), len(DEMO_DATES))).tolist()
        )

        df_grid = pd.DataFrame(
            np.array(init_matrix) > 0, index=DEMO_HOURS, columns=DEMO_DATES
        )

        edited_df = st.data_editor(
            df_grid,
            column_config={
                col: st.column_config.CheckboxColumn(col, default=False)
                for col in DEMO_DATES
            },
            use_container_width=True,
            height=380,
        )

        if st.button("💾 Save My Availability", type="primary"):
            save_matrix = edited_df.values.astype(int).tolist()
            with st.spinner("Saving response to Google Sheets..."):
                save_response("lab_demo", user_name, save_matrix)
            st.toast(f"Availability for {user_name} saved successfully!", icon="✅")
            st.rerun()

# ==========================================
# TAB 2: Team Results (Heatmap)
# ==========================================
with tab_results:
    st.subheader("Lab Availability Heatmap")

    responses = load_responses("lab_demo")

    if not responses:
        st.info("No responses submitted yet. Be the first to add your availability!")
    else:
        participants = list(responses.keys())
        matrices = [np.array(v) for v in responses.values()]
        total_matrix = sum(matrices)
        total_count = len(participants)

        col_summary, col_legend = st.columns([3, 1])

        with col_legend:
            st.markdown(f"**Responded ({total_count}):**")
            for p in participants:
                st.markdown(f"- `{p}`")

        with col_summary:
            fig = px.imshow(
                total_matrix,
                x=DEMO_DATES,
                y=DEMO_HOURS,
                labels=dict(x="Date", y="Time", color="Available Members"),
                color_continuous_scale="Blues",
                text_auto=True,
            )

            fig.update_layout(
                paper_bgcolor="white",
                plot_bgcolor="white",
                margin=dict(l=10, r=10, t=30, b=10),
                height=420,
            )

            st.plotly_chart(fig, use_container_width=True)

        # Calculate Golden Slots
        max_available = np.max(total_matrix)
        best_slots = np.argwhere(total_matrix == max_available)

        st.divider()
        if max_available == total_count:
            st.success(
                f"🎉 **Golden Slot:** All {total_count} members are available during these time slots!"
            )
        else:
            st.warning(
                f"⭐ **Optimal Options:** **{max_available} out of {total_count}** members can attend:"
            )

        cols_slots = st.columns(len(best_slots) if len(best_slots) <= 4 else 4)
        for idx, pos in enumerate(best_slots):
            r, c = pos[0], pos[1]
            with cols_slots[idx % 4]:
                st.info(f"📍 **{DEMO_DATES[c]}**\n\n⏰ **{DEMO_HOURS[r]}**")
