import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "Full_Segment_Analysis.csv"

if not CSV_PATH.exists():
    print("CSV not found.")
    exit()

df = pd.read_csv(CSV_PATH)

# Clean Columns
df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

# Ensure IoU is numeric
df['iou'] = pd.to_numeric(df['iou'], errors='coerce').fillna(0)
cols = ['manual_start', 'manual_end', 'predicted_start', 'predicted_end']
for c in cols:
    df[c] = pd.to_numeric(df[c], errors='coerce')

print(f"Loaded {len(df)} rows.")

# --- 1. Filter Data ---
# Structure Analysis usually focuses on VAD (Vocal Activity Detection).
# IoU is typically relevant for Manual Vocals.
df_vocals = df[df['manual_type'].str.contains('vocal', case=False, na=False)].copy()
df_instr = df[df['manual_type'].str.contains('inst', case=False, na=False)].copy()

# --- 2. Calculate IoU Metrics ---

# A. Per-Song Mean IoU (The numbers likely shown in the detailed table)
song_iou = df_vocals.groupby(['song_name', 'model'])['iou'].mean().reset_index()
# Rename for clarity
song_iou = song_iou.rename(columns={'iou': 'song_mean_iou'})

print("\n--- Per-Song Mean IoU (First 5) ---")
print(song_iou.head(10))

# B. Aggregate: Simple Mean of Songs (Mean of Means)
agg_mean_of_means = song_iou.groupby('model')['song_mean_iou'].mean()
agg_std_of_means = song_iou.groupby('model')['song_mean_iou'].std()

print("\n--- Aggregate: Simple Mean of Song Means ---")
print(agg_mean_of_means)
print("\n--- Aggregate: Std Dev of Song Means ---")
print(agg_std_of_means)
print("\n--- Aggregate: Median of Song Means ---")
print(agg_median_of_means)

# C. Aggregate: Pooled Segment Mean (Average of all segments irrespective of song)
pooled_mean = df_vocals.groupby('model')['iou'].mean()
print("\n--- Aggregate: Pooled Segment Mean ---")
print(pooled_mean)

# D. Aggregate: Duration Weighted Mean
df_vocals['duration'] = df_vocals['manual_end'] - df_vocals['manual_start']
def weighted_avg(x):
    if x['duration'].sum() == 0: return 0
    return np.average(x['iou'], weights=x['duration'])

weighted_mean = df_vocals.groupby('model').apply(weighted_avg)
print("\n--- Aggregate: Duration Weighted Mean ---")
print(weighted_mean)

# --- 3. Calculate FPR Metrics ---
# Count-based FPR: % of Instrumental Segments that have a Match (IoU > 0 implies predicted vocal overlap)
# Note: Full_Segment_Analysis.csv is derived from Hungarian matching. 
# If an instrumental segment overlaps a predicted vocal, it might be matched.
# A match here means "Predicted Vocal" overlapped "Manual Instrumental".
# So `iou > 0` (or existence of match) = False Positive.

# Check if 'iou' > 0 (matched)
df_instr['is_fp'] = df_instr['iou'] > IOU_MATCH_THRESHOLD if 'IOU_MATCH_THRESHOLD' in locals() else df_instr['iou'] > 0

song_fpr = df_instr.groupby(['song_name', 'model'])['is_fp'].mean().reset_index()
agg_fpr_mean = song_fpr.groupby('model')['is_fp'].mean()

print("\n--- Aggregate: Vocal FPR (Count-Based Mean of Songs) ---")
print(agg_fpr_mean)

# --- 4. Boundary Error ---
# Only for Matches (IoU > something, or just all matched vocals?)
# Start Error: abs(Manual Start - Predicted Start)
# End Error: abs(Manual Manual - Predicted End)
# Only applicable where prediction exists
df_matches = df_vocals.dropna(subset=['predicted_start'])
df_matches['start_err'] = (df_matches['manual_start'] - df_matches['predicted_start']).abs()
df_matches['end_err'] = (df_matches['manual_end'] - df_matches['predicted_end']).abs()
df_matches['boundary_err'] = (df_matches['start_err'] + df_matches['end_err']) / 2

avg_boundary_err = df_matches.groupby('model')['boundary_err'].mean()
print("\n--- Aggregate: Avg Boundary Error (sec) ---")
print(avg_boundary_err)
