import json
import csv
import pandas as pd
from pathlib import Path

# Config
BASE_DIR = Path(r"c:\Users\admin\Desktop\song analysis\data")
OUTPUT_CSV = BASE_DIR / "Manual_Segments_Ground_Truth.csv"

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return []

def main():
    print("Exporting Manual Ground Truth Data...")
    
    rows = []
    manual_folders = list(BASE_DIR.glob("*_Manual"))
    
    for m_folder in manual_folders:
        song = m_folder.name.replace("_Manual", "")
        file_path = m_folder / "song_structure.json"
        
        segments = load_json(file_path)
        if not segments:
            print(f"Skipping {song} (No data)")
            continue
            
        for i, seg in enumerate(segments):
            rows.append({
                "Song": song,
                "Segment Index": i + 1,
                "Start Time (s)": seg.get('start'),
                "End Time (s)": seg.get('end'),
                "Duration (s)": round(seg.get('end', 0) - seg.get('start', 0), 2),
                "Label": seg.get('label', ''),
                "Type": seg.get('type', 'unknown')
            })

    if rows:
        df = pd.DataFrame(rows)
        # Sort for cleanliness
        df = df.sort_values(by=['Song', 'Start Time (s)'])
        
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"Success! Exported {len(df)} segments to {OUTPUT_CSV}")
    else:
        print("No data found.")

if __name__ == "__main__":
    main()
