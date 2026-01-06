import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "Full_Segment_Analysis.csv"

if not CSV_PATH.exists():
    print(f"File not found: {CSV_PATH}")
    exit(1)

df = pd.read_csv(CSV_PATH)
print("Columns:", df.columns.tolist())
print("Head:")
print(df.head(2))
