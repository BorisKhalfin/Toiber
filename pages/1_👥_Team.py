import os
from pathlib import Path
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Team | Toiber Lab",
    page_icon="👥",
    layout="wide"
)

st.title("👥 Lab Team")
st.write("Meet the researchers, students, and staff of the Toiber Lab.")

st.divider()

AVATARS_DIR = Path("Avatars")
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]

def find_avatar_image(dir_path: Path, index: int):
    """Searches for Avatar{index} with various supported image extensions."""
    if not dir_path.exists():
        return None
    for ext in IMAGE_EXTENSIONS:
        img_path = dir_path / f"Avatar{index}{ext}"
        if img_path.exists():
            return img_path
    return None

# Placeholder team members data (20 blocks)
team_members = [
    {"name": "Dr. Debra Toiber", "role": "Principal Investigator"},
    {"name": "Dr. Shai Kaluski-Kopatch", "role": "Lab manager"},
    {"name": "Team Member 3", "role": "Ph.D. Candidate"},
    {"name": "Team Member 4", "role": "Ph.D. Candidate"},
    {"name": "Team Member 5", "role": "M.Sc. Student"},
    {"name": "Team Member 6", "role": "M.Sc. Student"},
    {"name": "Team Member 7", "role": "Lab Manager"},
    {"name": "Team Member 8", "role": "Research Assistant"},
    {"name": "Team Member 9", "role": "Graduate Student"},
    {"name": "Team Member 10", "role": "Graduate Student"},
    {"name": "Team Member 11", "role": "Undergraduate Student"},
    {"name": "Team Member 12", "role": "Undergraduate Student"},
    {"name": "Team Member 13", "role": "Visiting Scholar"},
    {"name": "Team Member 14", "role": "Bioinformatician"},
    {"name": "Team Member 15", "role": "Research Technician"},
    {"name": "Team Member 16", "role": "Alumni / Collaborator"},
    {"name": "Team Member 17", "role": "Student Researcher"},
    {"name": "Team Member 18", "role": "Student Researcher"},
    {"name": "Team Member 19", "role": "Lab Assistant"},
    {"name": "Team Member 20", "role": "Lab Assistant"},
]

# Display team grid (4 cards per row)
num_columns = 4

for row_start in range(0, len(team_members), num_columns):
    cols = st.columns(num_columns)
    for i in range(num_columns):
        member_idx = row_start + i
        if member_idx < len(team_members):
            member = team_members[member_idx]
            avatar_num = member_idx + 1
            img_path = find_avatar_image(AVATARS_DIR, avatar_num)

            with cols[i]:
                with st.container(border=True):
                    if img_path:
                        try:
                            img = Image.open(img_path)
                            st.image(img, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error loading Avatar{avatar_num}: {e}")
                    else:
                        st.image(
                            f"https://placehold.co/300x300/E2E8F0/475569?text=Avatar{avatar_num}",
                            use_container_width=True
                        )

                    st.markdown(f"**{member['name']}**")
                    st.caption(member['role'])
