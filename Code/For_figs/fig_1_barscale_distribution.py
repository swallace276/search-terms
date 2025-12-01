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
# BAR SCALE DISTRIBUTION ANALYSIS
# ===============================================

# First, let's understand what values we have
print("=== BAR SCALE DISTRIBUTION OVERVIEW ===")
print(f"Total events: {len(df)}")
print(f"Range: {df['BAR_Scale'].min()} to {df['BAR_Scale'].max()}")
print(f"\nValue frequencies:")
value_counts = df['BAR_Scale'].value_counts().sort_index()
print(value_counts)

# Check for zero values
zeros = len(df[df['BAR_Scale'] == 0])
print(f"\nEvents with BAR_Scale = 0: {zeros} ({zeros/len(df)*100:.2f}%)")

# ===============================================
# MULTIPLE VIEWS OF THE DISTRIBUTION
# ===============================================

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. Histogram - ALL values (including zeros if they exist)
axes[0, 0].hist(df['BAR_Scale'], bins=15, range=(-7, 7), edgecolor='black', color='steelblue', alpha=0.7)
axes[0, 0].axvline(x=0, color='red', linestyle='--', linewidth=2, label='Neutral (0)')
axes[0, 0].set_xlabel('BAR Scale (Conflict → Cooperation)', fontsize=12)
axes[0, 0].set_ylabel('Number of Events', fontsize=12)
axes[0, 0].set_title('Full Distribution (All Values)', fontsize=14, fontweight='bold')
axes[0, 0].grid(True, alpha=0.3, axis='y')
axes[0, 0].legend()
axes[0, 0].set_xlim(-7.5, 7.5)

# 2. Histogram - EXCLUDING zeros (to see the "true" distribution)
non_zero = df[df['BAR_Scale'] != 0]
axes[0, 1].hist(non_zero['BAR_Scale'], bins=14, range=(-7, 7), edgecolor='black', color='darkgreen', alpha=0.7)
axes[0, 1].axvline(x=0, color='red', linestyle='--', linewidth=2, label='Neutral (0)')
axes[0, 1].set_xlabel('BAR Scale (Conflict → Cooperation)', fontsize=12)
axes[0, 1].set_ylabel('Number of Events', fontsize=12)
axes[0, 1].set_title('Distribution (Excluding Zeros)', fontsize=14, fontweight='bold')
axes[0, 1].grid(True, alpha=0.3, axis='y')
axes[0, 1].legend()
axes[0, 1].set_xlim(-7.5, 7.5)

# 3. Bar chart showing exact counts for each BAR scale value
unique_values = df['BAR_Scale'].unique()
unique_values_sorted = sorted(unique_values)

value_counts = df['BAR_Scale'].value_counts().sort_index()
colors = ['red' if v < 0 else 'gray' if v == 0 else 'green' for v in value_counts.index]
axes[1, 0].bar(value_counts.index, value_counts.values, color=colors, alpha=0.7, edgecolor='black')
axes[1, 0].axvline(x=0, color='black', linestyle='--', linewidth=2)
axes[1, 0].set_xlabel('BAR Scale Value', fontsize=12)
axes[1, 0].set_ylabel('Number of Events', fontsize=12)
axes[1, 0].set_title('Exact Value Counts\n(Red=Conflict, Gray=Zero, Green=Cooperation)', fontsize=14, fontweight='bold')
axes[1, 0].grid(True, alpha=0.3, axis='y')
axes[1, 0].set_xlim(-7.5, 7.5)

# 4. Kernel density plot to show smooth distribution
ax4 = axes[1, 1]
# Exclude zeros for the density plot to get a cleaner view
df['BAR_Scale'].hist(bins=20, ax=ax4, density=True, alpha=0.5, color='steelblue', label='All values')
non_zero['BAR_Scale'].hist(bins=20, ax=ax4, density=True, alpha=0.5, color='darkgreen', label='Excluding zeros')
ax4.set_xlabel('BAR Scale (Conflict → Cooperation)', fontsize=12)
ax4.set_ylabel('Density', fontsize=12)
ax4.set_title('Probability Density\n(Smoothed Distribution)', fontsize=14, fontweight='bold')
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.axvline(x=0, color='red', linestyle='--', linewidth=1)

plt.tight_layout()

# Ensure Figs directory exists
os.makedirs('Figs', exist_ok=True)

# Save the figure BEFORE closing it
fig.savefig('Figs/Fig_1_BAR_Scale_Distribution.png', dpi=300, bbox_inches='tight')
plt.close(fig)

# ===============================================
# SUMMARY STATISTICS
# ===============================================

print("\n=== SUMMARY STATISTICS ===")
print(f"Mean: {df['BAR_Scale'].mean():.2f}")
print(f"Median: {df['BAR_Scale'].median():.2f}")
print(f"Std Dev: {df['BAR_Scale'].std():.2f}")
print(f"\nConflict events (< 0): {len(df[df['BAR_Scale'] < 0])} ({len(df[df['BAR_Scale'] < 0])/len(df)*100:.1f}%)")
print(f"Cooperation events (> 0): {len(df[df['BAR_Scale'] > 0])} ({len(df[df['BAR_Scale'] > 0])/len(df)*100:.1f}%)")
print(f"Zero/Neutral events: {zeros} ({zeros/len(df)*100:.1f}%)")

# Distribution by category
print("\n=== DISTRIBUTION BY MAGNITUDE ===")
print(f"High Conflict (-7 to -4): {len(df[(df['BAR_Scale'] >= -7) & (df['BAR_Scale'] <= -4)])} ({len(df[(df['BAR_Scale'] >= -7) & (df['BAR_Scale'] <= -4)])/len(df)*100:.1f}%)")
print(f"Moderate Conflict (-3 to -1): {len(df[(df['BAR_Scale'] >= -3) & (df['BAR_Scale'] <= -1)])} ({len(df[(df['BAR_Scale'] >= -3) & (df['BAR_Scale'] <= -1)])/len(df)*100:.1f}%)")
print(f"Neutral (0): {zeros} ({zeros/len(df)*100:.1f}%)")
print(f"Moderate Cooperation (1 to 3): {len(df[(df['BAR_Scale'] >= 1) & (df['BAR_Scale'] <= 3)])} ({len(df[(df['BAR_Scale'] >= 1) & (df['BAR_Scale'] <= 3)])/len(df)*100:.1f}%)")
print(f"High Cooperation (4 to 7): {len(df[(df['BAR_Scale'] >= 4) & (df['BAR_Scale'] <= 7)])} ({len(df[(df['BAR_Scale'] >= 4) & (df['BAR_Scale'] <= 7)])/len(df)*100:.1f}%)")

print(f"\nFigure saved to: Figs/Fig_1_BAR_Scale_Distribution.png")


