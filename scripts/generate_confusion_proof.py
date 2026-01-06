import json
import csv
import pandas as pd
from pathlib import Path

# Config
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_CSV = BASE_DIR / "Confusion_Proof_Log.csv"
OUTPUT_REPORT = BASE_DIR / "Confusion_Analysis_Report.md"

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return []

def check_overlap(s1, e1, s2, e2):
    # Returns overlap duration
    start = max(s1, s2)
    end = min(e1, e2)
    return max(0.0, end - start)

def is_instrumental(label, type_field):
    # Heuristic to detect instrumental sections in Manual Data
    # The 'type' field is usually 'instrumental' or 'vocals'
    # We also check the label text just in case
    if type_field and type_field.lower() == 'instrumental': return True
    text = label.lower()
    if 'instrumental' in text or 'interlude' in text or 'music' in text or 'bgm' in text:
        return True
    return False

def analyze_confusion():
    print("Generating Confusion Proof...")
    
    proof_rows = []
    
    # scan for manuals
    manual_folders = list(BASE_DIR.glob("*_Manual"))
    
    for m_folder in manual_folders:
        song = m_folder.name.replace("_Manual", "")
        
        m_data = load_json(m_folder / "song_structure.json")
        
        # Identify "Ground Truth Instrumental Zones"
        gt_instrumental_zones = []
        for seg in m_data:
            if is_instrumental(seg.get('label', ''), seg.get('type', '')):
                gt_instrumental_zones.append(seg)
                
        if not gt_instrumental_zones:
            print(f"Skipping {song} (No instrumental labeled in manual)")
            continue
            
        # Compare against Models
        for model in ["Demucs", "SAM"]:
            p_file = BASE_DIR / f"{song}_{model}" / "song_structure.json"
            if not p_file.exists(): continue
            
            p_data = load_json(p_file)
            
            # Check for violations
            for instr in gt_instrumental_zones:
                i_start = instr['start']
                i_end = instr['end']
                i_label = instr.get('label', 'Unnamed Instrumental')
                
                # Did model predict ANYTHING here?
                # Assumption: Model output is purely "Vocal Segments" unless stated otherwise.
                # (Demucs/SAM segmentation usually separates Vocals)
                
                for pred in p_data:
                    p_start = pred['start']
                    p_end = pred['end']
                    p_type = pred.get('type', 'vocals') # Default to vocals if unspecified
                    
                    # If model explicitly says "instrumental", it's NOT a confusion
                    if p_type.lower() == 'instrumental':
                        continue
                        
                    overlap = check_overlap(i_start, i_end, p_start, p_end)
                    
                    if overlap > 0.5: # Ignore tiny overlaps < 0.5s
                        overlap_start = max(i_start, p_start)
                        overlap_end = min(i_end, p_end)
                        proof_rows.append({
                            "Song": song,
                            "Model": model,
                            "Ground Truth Segment": i_label,
                            "GT Start": round(i_start, 1),
                            "GT End": round(i_end, 1),
                            "Model Prediction": "Vocal Segment", # Because it predicted a segment in an instrumental zone
                            "Pred Start": round(p_start, 1),
                            "Pred End": round(p_end, 1),
                            "Conflict Start": round(overlap_start, 1),
                            "Conflict End": round(overlap_end, 1),
                            "Confused Duration (s)": round(overlap, 2),
                            "Severity": "High" if overlap > 5.0 else "Low"
                        })

    # Save CSV
    df = pd.DataFrame(proof_rows)
    if not df.empty:
        df = df.sort_values(by=['Song', 'Model', 'GT Start'])
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"Saved proof logs to {OUTPUT_CSV}")
        
        # Generate Narrative Report
        generate_report(df)
    else:
        print("No significant confusions found.")

def generate_report(df):
    
    # Aggregations
    total_errors = len(df)
    by_model = df.groupby('Model')['Confused Duration (s)'].sum()
    
    sam_err = by_model.get('SAM', 0)
    demucs_err = by_model.get('Demucs', 0)
    
    ratio = sam_err / demucs_err if demucs_err > 0 else float('inf')
    
    top_offenders = df[df['Model'] == 'SAM'].sort_values('Confused Duration (s)', ascending=False).head(5)
    
    md = f"""
# Forensic Analysis: Instrumental Confusion (FPR) Explained

## 1. What is "FPR" in this context?
**False Positive Rate (FPR)** here answers: *"When the human explicitly marked a section as **Instrumental** (no singing), how often did the AI claim there were **Vocals**?"*

*   **Comparison**: We overlay the Manual "Instrumental" zones against the AI's predicted "Vocal" segments.
*   **The Logic**: Any overlap > 0.5 seconds is counted as a "Hallucination" or "Confusion".

## 2. The Verdict with Proof
We mathematically integrated the duration of these errors across all songs.

*   **SAM Total Hallucination Time**: {sam_err:.2f} seconds
*   **Demucs Total Hallucination Time**: {demucs_err:.2f} seconds
*   **Conclusion**: SAM hallucinates **{ratio:.1f}x more** than Demucs.

## 3. "Smokin' Gun" Examples (Top 5 SAM Hallucinations)
These are specific moments where **SAM** failed completely, hearing vocals where there were none.

| Song | Ground Truth (Instrumental) | Time Range | SAM Hallucination | Duration |
| :--- | :--- | :--- | :--- | :--- |
"""
    for _, row in top_offenders.iterrows():
        md += f"| {row['Song']} | **{row['Ground Truth Segment']}** | {row['GT Start']}s - {row['GT End']}s | Found Vocals | **{row['Confused Duration (s)']}s** |\n"
        
    md += f"""
## 4. Full Data Proof
A complete log of every single confusion event has been generated for your review.
**Path**: `data/Confusion_Proof_Log.csv`
"""
    
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"Report generated at {OUTPUT_REPORT}")

if __name__ == "__main__":
    analyze_confusion()
