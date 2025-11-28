import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path

# Add Code directory to path so imports work
code_dir = Path(__file__).parent
if str(code_dir) not in sys.path:
    sys.path.insert(0, str(code_dir))

from utils import get_user, full_process

st.title("Nexis-Uni Downloader")

uname = st.text_input("Enter username:")

# Get absolute path to basins.txt (one level up from Code/)
repo_root = code_dir.parent
basins_file = repo_root / "Data" / "basins.txt"

with open(basins_file, "r") as f:
    basins = [b.strip() for b in f.readlines()]

# Add checkbox for Single Event List mode
use_event_list = st.checkbox("Use Single Event List")

if use_event_list:
    # Load basins from CSV
    csv_path = st.text_input("Path to CSV file:", value=str(repo_root / "Data" / "single_event_basins.csv"))
    basin_column = st.text_input("Column name for basins:", value="BCODE")
    
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            if basin_column in df.columns:
                event_basins = df[basin_column].dropna().astype(str).str.strip().tolist()
                # Auto-populate the multiselect with basins from CSV
                chosen_basins = st.multiselect(
                    "Select basin code(s):", 
                    basins,
                    default=[b for b in event_basins if b in basins]  # Only include valid basins
                )
                st.info(f"Loaded {len(event_basins)} basins from CSV. {len(chosen_basins)} are valid.")
            else:
                st.error(f"Column '{basin_column}' not found in CSV")
                chosen_basins = st.multiselect("Select basin code(s):", basins)
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            chosen_basins = st.multiselect("Select basin code(s):", basins)
    else:
        st.warning(f"CSV file not found: {csv_path}")
        chosen_basins = st.multiselect("Select basin code(s):", basins)
else:
    # Regular multi-select mode
    chosen_basins = st.multiselect("Select basin code(s):", basins)

if st.button("Start Download"):
    if uname:
        if not chosen_basins:
            st.error("Please select at least one basin.")
        else:
            with st.spinner(f"Downloading {len(chosen_basins)} basin(s)..."):
                for i, basin in enumerate(chosen_basins, 1):
                    st.write(f"Processing basin {i}/{len(chosen_basins)}: {basin}")
                    paths, username = get_user(basin, uname)
                    full_process(basin, username, paths)
            st.success("Download completed successfully!")
    else:
        st.error("Please enter a username.")