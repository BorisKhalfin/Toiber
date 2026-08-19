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

# For external links (ORCID, PubMed, Google Scholar):
if member.get("link"):
    st.link_button("🔗 Personal Page", member["link"], use_container_width=True)

# For internal linsk (pages/Team/...):
if member.get("page"):
    st.page_link(member["page"], label="📄 Personal Page", use_container_width=True)

# Team members data with optional "link" and "bio" fields
team_members = [
    {
        "name": "Dr. Debra Toiber",
        "role": "Principal Investigator",
        "link": "https://orcid.org/0000-0002-1465-0130",
        "bio": ""
    },
    {
        "name": "Dr. Shai Kaluski-Kopatch",
        "role": "Lab manager",
        "link": "",
        "bio": ""
    },
    {
        "name": "Dr. Ekaterina Eremenko",
        "role": "Research associate",
        "link": "",
        "bio": ""
    },
    {
        "name": "Dr. Boris Khalfin",
        "role": "Researcher",
        "page": "pages/Team/Dr. Boris Khalfin.py",
        "bio": ""
    },
    {
        "name": "Dr. Daniel Stein",
        "role": "Postdoctoral fellow",
        "link": "",
        "bio": ""
    },
    {
        "name": "Daniela Eisurovich",
        "role": "Ph.D. Student",
        "link": "",
        "bio": ""
    },
    {"name": "Team Member 7", "role": "Lab Manager", "link": "", "bio": ""},
    {"name": "Team Member 8", "role": "Research Assistant", "link": "", "bio": ""},
    {"name": "Team Member 9", "role": "Graduate Student", "link": "", "bio": ""},
    {"name": "Team Member 10", "role": "Graduate Student", "link": "", "bio": ""},
    {"name": "Team Member 11", "role": "Undergraduate Student", "link": "", "bio": ""},
    {"name": "Team Member 12", "role": "Undergraduate Student", "link": "", "bio": ""},
    {"name": "Team Member 13", "role": "Visiting Scholar", "link": "", "bio": ""},
    {"name": "Team Member 14", "role": "Bioinformatician", "link": "", "bio": ""},
    {"name": "Team Member 15", "role": "Research Technician", "link": "", "bio": ""},
    {"name": "Team Member 16", "role": "Alumni / Collaborator", "link": "", "bio": ""},
    {"name": "Team Member 17", "role": "Student Researcher", "link": "", "bio": ""},
    {"name": "Team Member 18", "role": "Student Researcher", "link": "", "bio": ""},
    {"name": "Team Member 19", "role": "Lab Assistant", "link": "", "bio": ""},
    {"name": "Team Member 20", "role": "Lab Assistant", "link": "", "bio": ""},
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

                    # Display optional biography
                    if member.get("bio"):
                        st.write(member["bio"])

                    # Display optional profile button
                    if member.get("link"):
                        st.link_button("🔗 Personal Page", member["link"], use_container_width=True)
