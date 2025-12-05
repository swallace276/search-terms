"""
Simple Basin Mapper
====================
Maps transboundary river basins from shapefile with highlighting
"""
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend (no display required)

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

# Load the basin shapefile
gdf = gpd.read_file('Data/Basin_shapefile/BasinMaster313_20240807.shp')

# Load the basin status sheet
status_df = pd.read_excel('Data/single_event_basins_with_notes.xlsx')

# Filter to basins where both searches are complete
complete_basins = status_df[
    (status_df['status_new_search'] == 'complete') & 
    (status_df['status_old_search'] == 'complete')
]

# Get list of basin codes
basins_to_map = complete_basins['BCODE'].tolist()

print(f"Found {len(basins_to_map)} basins with both searches complete:")
print(basins_to_map)


# Create a column to indicate if basin is in our study
gdf['in_study'] = gdf['BCODE'].isin(basins_to_map)

# Create the map
fig, ax = plt.subplots(figsize=(16, 10))

# Plot all basins in light gray
gdf[~gdf['in_study']].plot(ax=ax, color='lightgray', edgecolor='white', linewidth=0.5)

# Plot study basins in blue
gdf[gdf['in_study']].plot(ax=ax, color='#2E86AB', edgecolor='darkblue', linewidth=1)

# Add labels for study basins
study_basins = gdf[gdf['in_study']]
for idx, row in study_basins.iterrows():
    # Get the centroid of each basin for label placement
    centroid = row['geometry'].centroid
    
    # Add text label with white background for visibility
    ax.text(centroid.x, centroid.y, row['BCODE'], 
            fontsize=9, 
            fontweight='bold',
            ha='center', 
            va='center',
            color='white',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='darkblue', edgecolor='none', alpha=0.8))


# Add title
plt.title('Transboundary River Basins: Single-Event Basin Analysis\n9 Basins Under Study', 
          fontsize=16, fontweight='bold', pad=20)

# Remove axes
ax.set_axis_off()

# Add a simple legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#2E86AB', edgecolor='darkblue', label=f'Study Basins (n={len(basins_to_map)})'),
    Patch(facecolor='lightgray', edgecolor='white', label=f'Other Basins (n={313-len(basins_to_map)})')
]
ax.legend(handles=legend_elements, loc='lower left', fontsize=12, framealpha=0.9)

# Save the map
plt.tight_layout()
fig.savefig('Figs/Fig_4_map_of_study_basins.png', dpi=300, bbox_inches='tight')
plt.close(fig)
