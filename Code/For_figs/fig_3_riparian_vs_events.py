import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend to avoid Tcl/Tk issues
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import os

# read excel (downloaded from Shared Waters Lab's shared Box drive)
df = pd.read_excel('Data/Events_2008.xls')

# Load spatial data
spatial_df_path = 'Data/Basins_2024.csv'
spatial_df = pd.read_csv(spatial_df_path)

# ===============================================
# PREPARE DATA: BASIN FREQUENCY
# ===============================================

# Calculate value frequencies for the 'BCode' column
bcode_counts = df['BCode'].value_counts()
basin_frequency_df = bcode_counts.to_frame('frequency').reset_index()
basin_frequency_df.columns = ['BCode', 'frequency']

# Remove UNKN basin
basin_frequency_df = basin_frequency_df[basin_frequency_df['BCode'] != 'UNKN']

# ===============================================
# PREPARE DATA: RIPARIAN COUNTRIES
# ===============================================

# Build dictionary of basin -> riparian count
df_riparian_events = {}

# iterate through all bcodes
for basin in basin_frequency_df['BCode']:
    # get the event frequency for this basin
    event_frequency = basin_frequency_df[basin_frequency_df['BCode'] == basin]['frequency'].iloc[0]
    
    # get the riparian countries for this basin - with error checking
    matching_rows = spatial_df[spatial_df['BCODE'] == basin]
    
    if len(matching_rows) > 0:
        # Basin found in spatial data
        riparian_value = matching_rows['Riparian_C'].iloc[0]
        countries = riparian_value.split(',')
        # clean up whitespace
        countries = [country.strip() for country in countries]
        count_riparian_countries = len(countries)
    else:
        # Basin not found in spatial data
        print(f"Warning: Basin {basin} not found in spatial data")
        countries = []
        count_riparian_countries = 0
    
    # store in dictionary
    df_riparian_events[basin] = {
        'BCODE': basin,
        'event_frequency': event_frequency,
        'riparian_countries': countries,
        'riparian_count': count_riparian_countries
    }

# Convert to DataFrame
riparian_events = pd.DataFrame(df_riparian_events).T
riparian_events.reset_index(drop=True, inplace=True)

# Convert to numeric
riparian_events['riparian_count'] = pd.to_numeric(riparian_events['riparian_count'], errors='coerce')
riparian_events['event_frequency'] = pd.to_numeric(riparian_events['event_frequency'], errors='coerce')

# ===============================================
# OUTLIER DETECTION
# ===============================================

def find_outliers_iqr(data, column):
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = data[(data[column] < lower_bound) | (data[column] > upper_bound)]
    return outliers

# Find outliers in both dimensions
riparian_outliers = find_outliers_iqr(riparian_events, 'riparian_count')
event_outliers = find_outliers_iqr(riparian_events, 'event_frequency')

# Get top outliers
if len(riparian_outliers) > 0:
    top_riparian_outliers = riparian_outliers.sort_values('riparian_count', ascending=False).head(3)
else:
    top_riparian_outliers = pd.DataFrame()

if len(event_outliers) > 0:
    top_event_outliers = event_outliers.sort_values('event_frequency', ascending=False).head(3)
else:
    top_event_outliers = pd.DataFrame()

# ===============================================
# VISUALIZATION
# ===============================================

# Create plot with extreme cases highlighted
fig, ax = plt.subplots(figsize=(16, 10))
ax.scatter(riparian_events['riparian_count'], riparian_events['event_frequency'],
            alpha=0.6, s=100, color='steelblue', edgecolors='white', linewidth=0.5, label='Basin')

# Highlight only the most extreme outliers
if len(top_riparian_outliers) > 0:
    ax.scatter(top_riparian_outliers['riparian_count'], top_riparian_outliers['event_frequency'],
                s=200, color='red', marker='o', edgecolors='black', linewidth=0.8, label='Most riparian countries')

if len(top_event_outliers) > 0:
    ax.scatter(top_event_outliers['riparian_count'], top_event_outliers['event_frequency'],
                s=200, color='orange', marker='^', edgecolors='black', linewidth=0.8, label='Most events')

# Label only these extreme cases
if len(top_riparian_outliers) > 0 or len(top_event_outliers) > 0:
    all_extreme = pd.concat([top_riparian_outliers, top_event_outliers]).drop_duplicates(subset=['BCODE'])
    for _, row in all_extreme.iterrows():
        ax.annotate(row['BCODE'], (row['riparian_count'], row['event_frequency']),
                     xytext=(5, 5), textcoords='offset points', fontsize=14, color='darkred', weight='bold')

ax.set_xticks(range(0, int(riparian_events['riparian_count'].max()) + 1, 2))
ax.set_xlabel('Number of Riparian Countries', fontsize=16)
ax.set_ylabel('Number of Events', fontsize=16)
ax.set_title('Number of Riparian Countries vs Number of Events: Exceptional Cases', fontsize=20)
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()

# Ensure Figs directory exists
os.makedirs('Figs', exist_ok=True)

# Save the figure BEFORE closing it
fig.savefig('Figs/Fig_3_Riparian_Countries_vs_Events.png', dpi=300, bbox_inches='tight')
plt.close(fig)

print("=== RIPARIAN COUNTRIES VS EVENTS ANALYSIS ===")
print(f"Total basins analyzed: {len(riparian_events)}")
print(f"Riparian count range: {riparian_events['riparian_count'].min()} to {riparian_events['riparian_count'].max()}")
print(f"Event frequency range: {riparian_events['event_frequency'].min()} to {riparian_events['event_frequency'].max()}")
print(f"\nFigure saved to: Figs/Fig_3_Riparian_Countries_vs_Events.png")


