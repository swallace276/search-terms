import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path
from datetime import datetime

# Add Code directory to path so imports work
code_dir = Path(__file__).parent
if str(code_dir) not in sys.path:
    sys.path.insert(0, str(code_dir))

from utils import get_user, full_process

st.title("Nexis-Uni Downloader")

uname = st.text_input("Enter username:")

# Add search protocol toggle
search_protocol = st.radio(
    "Search Protocol:",
    options=["2025 Protocol (New Search)", "2008 Protocol (Old Search)"],
    index=0
)

use_new_search = "2025" in search_protocol

# Get absolute path to basins.txt (one level up from Code/)
repo_root = code_dir.parent
basins_file = repo_root / "Data" / "basins.txt"

with open(basins_file, "r") as f:
    basins = [b.strip() for b in f.readlines()]

# Add checkbox for Single Event List mode
use_event_list = st.checkbox("Use Single Event List")

# Initialize variables
event_list_df = None
csv_path = None

if use_event_list:
    # Default CSV path
    default_csv = str(repo_root / "Data" / "single_event_basins.csv")
    csv_path_input = st.text_input("Path to CSV file:", value=default_csv)
    basin_column = st.text_input("Column name for basins:", value="BCODE")
    
    if os.path.exists(csv_path_input):
        try:
            event_list_df = pd.read_csv(csv_path_input)
            csv_path = csv_path_input  # Store for later updates
            
            if basin_column in event_list_df.columns:
                # Add status columns if they don't exist (separate for new and old)
                if 'status_new_search' not in event_list_df.columns:
                    event_list_df['status_new_search'] = 'pending'
                if 'status_old_search' not in event_list_df.columns:
                    event_list_df['status_old_search'] = 'pending'
                if 'completed_timestamp_new' not in event_list_df.columns:
                    event_list_df['completed_timestamp_new'] = ''
                if 'completed_timestamp_old' not in event_list_df.columns:
                    event_list_df['completed_timestamp_old'] = ''
                
                # Save the updated dataframe with new columns
                event_list_df.to_csv(csv_path, index=False)
                
                # Determine which status column to check based on protocol
                status_col = 'status_new_search' if use_new_search else 'status_old_search'
                
                # Filter out completed basins for the selected protocol
                pending_df = event_list_df[event_list_df[status_col] != 'complete']
                event_basins = pending_df[basin_column].dropna().astype(str).str.strip().tolist()
                
                # Count completed vs pending for this protocol
                completed_count = len(event_list_df[event_list_df[status_col] == 'complete'])
                total_count = len(event_list_df)
                
                chosen_basins = st.multiselect(
                    "Select basin code(s):", 
                    basins,
                    default=[b for b in event_basins if b in basins]
                )
                
                protocol_display = "new search" if use_new_search else "old search"
                st.info(f"Loaded {len(event_basins)} pending basins for {protocol_display} ({completed_count}/{total_count} already complete). {len(chosen_basins)} are valid.")
                
                # Show current status
                if st.checkbox("Show current status"):
                    display_cols = [basin_column, 'status_new_search', 'completed_timestamp_new', 
                                   'status_old_search', 'completed_timestamp_old']
                    st.dataframe(event_list_df[display_cols])
            else:
                st.error(f"Column '{basin_column}' not found in CSV")
                chosen_basins = st.multiselect("Select basin code(s):", basins)
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            chosen_basins = st.multiselect("Select basin code(s):", basins)
    else:
        st.warning(f"CSV file not found: {csv_path_input}")
        chosen_basins = st.multiselect("Select basin code(s):", basins)
else:
    chosen_basins = st.multiselect("Select basin code(s):", basins)

if st.button("Start Download"):
    if uname:
        if not chosen_basins:
            st.error("Please select at least one basin.")
        else:
            protocol_name = "New" if use_new_search else "Old"
            
            # Determine which columns to update based on protocol
            status_col = 'status_new_search' if use_new_search else 'status_old_search'
            timestamp_col = 'completed_timestamp_new' if use_new_search else 'completed_timestamp_old'
            
            # Create progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner(f"Downloading {len(chosen_basins)} basin(s) using {protocol_name} Search..."):
                for i, basin in enumerate(chosen_basins, 1):
                    status_text.write(f"Processing basin {i}/{len(chosen_basins)}: {basin}")
                    
                    try:
                        paths, username = get_user(basin, uname, use_new_search=use_new_search)
                        success = full_process(basin, username, paths, use_new_search=use_new_search)
                        
                        # Update CSV status if using event list
                        if use_event_list and csv_path:
                            df_updated = pd.read_csv(csv_path)
                            mask = df_updated[basin_column] == basin
                            
                            if success:
                                df_updated.loc[mask, status_col] = 'complete'
                                st.success(f"✅ {basin} completed ({protocol_name} search) and marked in CSV")
                            else:
                                df_updated.loc[mask, status_col] = 'failed'
                                st.warning(f"⚠️ {basin} failed ({protocol_name} search) and marked in CSV")
                            
                            df_updated.loc[mask, timestamp_col] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            df_updated.to_csv(csv_path, index=False)

                    except Exception as e:
                        st.error(f"❌ Error processing {basin}: {str(e)}")
                        
                        # Mark as failed in CSV
                        if use_event_list and csv_path:
                            df_updated = pd.read_csv(csv_path)
                            mask = df_updated[basin_column] == basin
                            df_updated.loc[mask, status_col] = 'failed'
                            df_updated.loc[mask, timestamp_col] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            df_updated.to_csv(csv_path, index=False)                            
                    
                    # Update progress bar
                    progress_bar.progress(i / len(chosen_basins))
            
            st.success("All downloads completed!")
            
            # Offer to download updated CSV
            if use_event_list and csv_path:
                final_df = pd.read_csv(csv_path)
                csv_download = final_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Updated CSV with Status",
                    data=csv_download,
                    file_name=f"event_list_updated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime='text/csv'
                )
    else:
        st.error("Please enter a username.")