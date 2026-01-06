import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "advanced_metrics.csv"

if not CSV_PATH.exists():
    print("CSV not found.")
    exit()

df = pd.read_csv(CSV_PATH)
# Calculate Aggregates
# Song-Level Mean (This corresponds to 'Simple Mean of Song Means' in the previous analysis)
# We can also check if duration weighting is needed, but 'mean_iou' in this CSV is already per-song.
means = df.groupby('Model')[['mean_iou', 'median_iou', 'fpr_time', 'fpr_count']].mean()
stds = df.groupby('Model')[['mean_iou', 'median_iou', 'fpr_time', 'fpr_count']].std()

print("\n--- Aggregate Metrics (Means) ---")
print(means)
print("\n--- Aggregate Metrics (Std Devs) ---")
print(stds)

print("\n--- Markdown Table for Per-Song Analysis ---")
print("| Song Name | Model | Mean IoU | Vocal FPR (Time) |")
print("| :--- | :--- | :--- | :--- |")
for _, row in df.sort_values(['Song', 'Model']).iterrows():
    print(f"| {row['Song']} | {row['Model']} | {row['mean_iou']:.3f} | {row['fpr_time']:.3f} |")
