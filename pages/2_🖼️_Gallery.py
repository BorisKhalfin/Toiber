import os
from pathlib import Path
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Gallery | Toiber Lab",
    page_icon="🖼️",
    layout="wide"
)

st.title("🖼️ Lab Gallery")
st.write("Moments from lab life, conferences, team lunches, and celebrations.")

st.divider()

# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}

# Path to the Photos directory
PHOTOS_DIR = Path("Photos")

def get_images_from_dir(directory: Path):
    """Returns a sorted list of image file paths from a directory (non-recursive)."""
    if not directory.exists() or not directory.is_dir():
        return []
    images = [
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ]
    return sorted(images)

def render_image_grid(image_paths, num_columns=3):
    """Renders images in a responsive grid layout."""
    if not image_paths:
        return
    cols = st.columns(num_columns)
    for index, img_path in enumerate(image_paths):
        col = cols[index % num_columns]
        with col:
            try:
                img = Image.open(img_path)
                st.image(
                    img,
                    caption=img_path.name,
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error loading {img_path.name}: {e}")

if not PHOTOS_DIR.exists():
    st.info("📌 The `Photos/` directory was not found in the repository root. Please create a `Photos` folder and add your subfolders and images there.")
else:
    # 1. Subdirectories inside Photos
    subdirs = sorted([d for d in PHOTOS_DIR.iterdir() if d.is_dir()])
    
    has_content = False

    for subdir in subdirs:
        images = get_images_from_dir(subdir)
        if images:
            has_content = True
            # Clean folder name for display
            folder_display_name = subdir.name.replace("_", " ").title()
            st.subheader(f"📁 {folder_display_name}")
            render_image_grid(images, num_columns=3)
            st.markdown("<br>", unsafe_allow_html=True)

    # 2. Photos directly in the root Photos directory
    root_images = get_images_from_dir(PHOTOS_DIR)
    if root_images:
        has_content = True
        st.subheader("📁 General Photos")
        render_image_grid(root_images, num_columns=3)

    if not has_content:
        st.warning("No image files found inside the `Photos/` directory or its subdirectories.")
