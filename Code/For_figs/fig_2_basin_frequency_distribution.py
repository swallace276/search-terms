import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend to avoid Tcl/Tk issues
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import os

# read excel (downloaded from Shared Waters Lab's shared Box drive)
df = pd.read_excel('Data/Events_2008.xls')

# ===============================================
# BASIN FREQUENCY DISTRIBUTION
# ===============================================

# Calculate value frequencies for the 'BCode' column
bcode_counts = df['BCode'].value_counts()

basin_frequency_df = bcode_counts.to_frame('frequency').reset_index()

# Rename the columns for clarity
basin_frequency_df.columns = ['BCode', 'frequency']

print("=== BASIN FREQUENCY DISTRIBUTION ===")
print(f"Total basins with events: {len(basin_frequency_df)}")
print(f"Frequency range: {basin_frequency_df['frequency'].min()} to {basin_frequency_df['frequency'].max()}")

# ===============================================
# VISUALIZATION
# ===============================================

# Alternative histogram with log scale for better visualization of the distribution
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Regular histogram
ax1.hist(basin_frequency_df['frequency'], bins=30, edgecolor='white', color='seagreen', alpha=0.7)
ax1.set_xlabel('Number of Events (Frequency)', fontsize=12)
ax1.set_ylabel('Number of Basins', fontsize=12)
ax1.set_title('Basin Frequency Distribution (Linear Scale)', fontsize=14)
ax1.grid(True, alpha=0.3)

# Log scale histogram for better visualization of the tail
ax2.hist(basin_frequency_df['frequency'], bins=30, edgecolor='white', color='steelblue', alpha=0.7)
ax2.set_xlabel('Number of Events (Frequency)', fontsize=12)
ax2.set_ylabel('Number of Basins', fontsize=12)
ax2.set_title('Basin Frequency Distribution (Log Scale)', fontsize=14)
ax2.set_yscale('log')
ax2.grid(True, alpha=0.3)

plt.tight_layout()

# Ensure Figs directory exists
os.makedirs('Figs', exist_ok=True)

# Save the figure BEFORE closing it
fig.savefig('Figs/Fig_2_Basin_Frequency_Distribution.png', dpi=300, bbox_inches='tight')
plt.close(fig)

# Show the distribution of frequencies in different ranges
print("\nDistribution by frequency ranges:")
print("=" * 40)
print(f"1-10 events: {len(basin_frequency_df[basin_frequency_df['frequency'] <= 10])} basins")
print(f"11-50 events: {len(basin_frequency_df[(basin_frequency_df['frequency'] > 10) & (basin_frequency_df['frequency'] <= 50)])} basins")
print(f"51-100 events: {len(basin_frequency_df[(basin_frequency_df['frequency'] > 50) & (basin_frequency_df['frequency'] <= 100)])} basins")
print(f"101-500 events: {len(basin_frequency_df[(basin_frequency_df['frequency'] > 100) & (basin_frequency_df['frequency'] <= 500)])} basins")
print(f"500+ events: {len(basin_frequency_df[basin_frequency_df['frequency'] > 500])} basins")

print(f"\nFigure saved to: Figs/Fig_2_Basin_Frequency_Distribution.png")


