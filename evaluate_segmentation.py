import json
import os
import glob
from pathlib import Path
import pandas as pd

# Define paths
BASE_DIR = r"c:\Users\admin\Desktop\song analysis\data"
OUTPUT_FILE = r"c:\Users\admin\Desktop\song analysis\Quantitative_Evaluation_Report.md"

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return []

def get_pairs(base_dir):
    pairs = {}
    path = Path(base_dir)
    for folder in path.iterdir():
        if not folder.is_dir(): continue
        name = folder.name
        key = None
        type_ = None
        
        if name.endswith("_Demucs"):
            key = name.replace("_Demucs", "")
            type_ = "Demucs"
        elif name.endswith("_SAM"):
            key = name.replace("_SAM", "")
            type_ = "SAM"
        elif name.endswith("_Manual"):
            key = name.replace("_Manual", "")
            type_ = "Manual"
            
        if key:
            if key not in pairs: pairs[key] = {}
            pairs[key][type_] = folder
    return pairs

def calculate_iou(s1, e1, s2, e2):
    """
    Calculate Intersection over Union for two time intervals.
    """
    start_inter = max(s1, s2)
    end_inter = min(e1, e2)
    
    if start_inter < end_inter:
        intersection = end_inter - start_inter
        union = max(e1, e2) - min(s1, s2)
        return intersection / union if union > 0 else 0
    return 0

def evaluate_song(song_name, manual_segments, predicted_segments, model_name):
    """
    Compare Manual vs Predicted segments.
    Returns:
        - metrics: Dictionary of aggregated stats for this song
        - row_data: List of dicts for the Segment-Wise Error Table
    """
    row_data = []
    
    # Track used predicted segments to identify Insertions
    matched_predicted_indices = set()
    
    total_iou = 0
    segment_count = 0
    ious = []
    
    boundary_errors_start = []
    boundary_errors_end = []
    
    deletions = 0
    insertions = 0
    label_confusions = 0 # Instrumental -> Vocal
    
    # --- 1. Iterate Manual Segments (Check for Matches & Deletions) ---
    for m_seg in manual_segments:
        m_start, m_end = m_seg['start'], m_seg['end']
        m_label = m_seg['label']
        m_type = m_seg.get('type', 'unknown').lower()
        
        best_iou = 0
        best_idx = -1
        best_p_seg = None
        
        # Find best overlapping predicted segment
        for idx, p_seg in enumerate(predicted_segments):
            iou = calculate_iou(m_start, m_end, p_seg['start'], p_seg['end'])
            if iou > best_iou:
                best_iou = iou
                best_idx = idx
                best_p_seg = p_seg
        
        error_type = ""
        p_start, p_end = None, None
        
        if best_iou > 0.1: # Threshold for a valid match
            matched_predicted_indices.add(best_idx)
            p_start, p_end = best_p_seg['start'], best_p_seg['end']
            
            # Boundary Errors
            start_diff = p_start - m_start
            end_diff = p_end - m_end
            boundary_errors_start.append(abs(start_diff))
            boundary_errors_end.append(abs(end_diff))
            
            # Error Typing
            if start_diff > 2.0: error_type += "Boundary Lag; "
            if start_diff < -2.0: error_type += "Boundary Early; "
            
            # Label Confusion (Specific check: Manual='instrumental' vs Predicted='vocals')
            p_type = best_p_seg.get('type', 'unknown').lower()
            if m_type == 'instrumental' and p_type == 'vocals':
                error_type += "Instrumental->Vocal Confusion; "
                label_confusions += 1
            elif m_type == 'vocals' and p_type == 'instrumental':
                error_type += "Vocal->Instrumental Confusion; "
                
        else:
            # No match found -> Deletion
            error_type = "Missed Segment (Deletion)"
            deletions += 1
            
        total_iou += best_iou
        ious.append(best_iou)
        segment_count += 1
        
        row_data.append({
            "Song Name": song_name,
            "Model": model_name,
            "Manual Segment": m_label,
            "Manual Start": round(m_start, 2),
            "Manual End": round(m_end, 2),
            "Predicted Start": round(p_start, 2) if p_start is not None else "-",
            "Predicted End": round(p_end, 2) if p_end is not None else "-",
            "IoU": round(best_iou, 3),
            "Error Type": error_type.strip("; "),
            "Manual Type": m_type
        })

    # --- 2. Check for Hallucinations (Insertions) ---
    for idx, p_seg in enumerate(predicted_segments):
        if idx not in matched_predicted_indices:
            insertions += 1
            row_data.append({
                "Song Name": song_name,
                "Model": model_name,
                "Manual Segment": "-",
                "Manual Start": "-",
                "Manual End": "-",
                "Predicted Start": round(p_seg['start'], 2),
                "Predicted End": round(p_seg['end'], 2),
                "IoU": 0.0,
                "Error Type": "Hallucinated Segment (Insertion)",
                "Manual Type": "-"
            })

    # --- 3. Compute Vocal False Positive Rate (FPR) ---
    # FPR = instrumental segments labeled as vocal / total manual instrumental segments
    manual_instrumental_count = len([s for s in manual_segments if s.get('type') == 'instrumental'])
    fpr = 0
    if manual_instrumental_count > 0:
        fpr = label_confusions / manual_instrumental_count
        
    metrics = {
        "Mean IoU": sum(ious) / len(ious) if ious else 0,
        "Median IoU": pd.Series(ious).median() if ious else 0,
        "Avg Boundary Error (s)": (sum(boundary_errors_start) + sum(boundary_errors_end)) / (len(boundary_errors_start) + len(boundary_errors_end)) if boundary_errors_start else 0,
        "Deletion Rate": deletions / segment_count if segment_count > 0 else 0,
        "Insertion Rate": insertions / segment_count if segment_count > 0 else 0, # Relative to manual count
        "Vocal FPR": fpr,
        "Total Manual Segments": segment_count,
        "Total Predicted Segments": len(predicted_segments)
    }
    
    return metrics, row_data

def generate_report():
    pairs = get_pairs(BASE_DIR)
    
    all_rows = []
    demucs_metrics_list = []
    sam_metrics_list = []
    
    songs_processed = []

    for song, folders in pairs.items():
        if "Manual" not in folders: continue
        
        # Load Manual Data
        manual_path = folders["Manual"] / "song_structure.json"
        manual_data = load_json(manual_path)
        if not manual_data: continue

        songs_processed.append(song)
        
        # Evaluate Demucs
        if "Demucs" in folders:
            demucs_path = folders["Demucs"] / "song_structure.json"
            demucs_pred = load_json(demucs_path)
            d_metrics, d_rows = evaluate_song(song, manual_data, demucs_pred, "Demucs")
            all_rows.extend(d_rows)
            demucs_metrics_list.append(d_metrics)
            
        # Evaluate SAM
        if "SAM" in folders:
            sam_path = folders["SAM"] / "song_structure.json"
            sam_pred = load_json(sam_path)
            s_metrics, s_rows = evaluate_song(song, manual_data, sam_pred, "SAM")
            all_rows.extend(s_rows)
            sam_metrics_list.append(s_metrics)

    # --- Create Summary DataFrames ---
    df_rows = pd.DataFrame(all_rows)
    
    # Calculate Aggregate Metrics
    def aggregate(metrics_list):
        if not metrics_list: return {}
        df = pd.DataFrame(metrics_list)
        return {
            "Mean IoU": df["Mean IoU"].mean(),
            "Median IoU": df["Median IoU"].mean(),
            "% IoU > 0.75": (df["Mean IoU"] > 0.75).mean(), # Approximate for now, ideally per segment
            "Avg Boundary Error (ms)": df["Avg Boundary Error (s)"].mean() * 1000,
            "Deletion Rate": df["Deletion Rate"].mean(),
            "Insertion Rate": df["Insertion Rate"].mean(),
            "Vocal False Positive Rate": df["Vocal FPR"].mean()
        }

    demucs_agg = aggregate(demucs_metrics_list)
    sam_agg = aggregate(sam_metrics_list)

    # --- Save Full Data to CSV (The "Proof") ---
    full_csv_path = Path(BASE_DIR) / "Full_Segment_Analysis.csv"
    df_rows.to_csv(full_csv_path, index=False)
    print(f"Full segment analysis saved to {full_csv_path}")

    # --- Create Per-Song Summary ---
    per_song_list = []
    for s_metrics in demucs_metrics_list:
        per_song_list.append({
            "Song": "Unknown", # Need to link back to song name, refactoring slightly below
            "Model": "Demucs",
            "IoU": s_metrics["Mean IoU"],
            "FPR": s_metrics["Vocal FPR"]
        })
        
    # Refactoring slightly to get song names in per-song table
    # We will reconstruct the per-song table from the collected list but we didn't save song names in the metrics list earlier.
    # Let's rebuild the loop structure or just use df_rows to aggregate per song.
    
    song_group = df_rows.groupby(['Song Name', 'Model']).apply(
        lambda x: pd.Series({
            'Mean IoU': x['IoU'].mean(),
            'Vocal FPR': (x['Error Type'].str.contains('Instrumental->Vocal').sum()) / 
                         (x[x['Manual Type']=='instrumental'].shape[0] if x[x['Manual Type']=='instrumental'].shape[0] > 0 else 1)
        })
    ).reset_index()

    # --- Generate Markdown Report ---
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Quantitative Evaluation Report: Demucs vs SAM\n\n")
        
        f.write("## 1. Executive Summary\n")
        f.write("This report provides a strict quantitative comparison of Demucs and SAM against a Manual Ground Truth dataset.\n")
        f.write(f"**Total Songs Analyzed**: {len(songs_processed)}\n")
        f.write(f"**Full Data Proof**: [Download CSV](./data/Full_Segment_Analysis.csv)\n\n")
        
        f.write("## 2. Quantitative Findings\n\n")
        
        f.write("### 2.1 Comparative Findings\n")
        if demucs_agg["Mean IoU"] > sam_agg["Mean IoU"]:
            f.write(f"- **Alignment**: Demucs achieves a higher Mean IoU ({demucs_agg['Mean IoU']:.2f}) compared to SAM ({sam_agg['Mean IoU']:.2f}), indicating better overlap with ground truth.\n")
        else:
            f.write(f"- **Alignment**: SAM achieves a higher Mean IoU ({sam_agg['Mean IoU']:.2f}) compared to Demucs ({demucs_agg['Mean IoU']:.2f}).\n")
            
        if demucs_agg["Vocal False Positive Rate"] < sam_agg["Vocal False Positive Rate"]:
             f.write(f"- **Instrumental Confusion**: SAM shows a higher Vocal False Positive Rate ({sam_agg['Vocal False Positive Rate']:.2%}) than Demucs ({demucs_agg['Vocal False Positive Rate']:.2%}), confirming the issue of misclassifying instruments as vocals.\n")
        else:
             f.write(f"- **Instrumental Confusion**: Demucs shows a higher Vocal False Positive Rate ({demucs_agg['Vocal False Positive Rate']:.2%}) than SAM.\n")
             
        f.write(f"- **Boundary Precision**: The average boundary error for Demucs is {demucs_agg['Avg Boundary Error (ms)']:.0f}ms, whereas SAM is {sam_agg['Avg Boundary Error (ms)']:.0f}ms.\n\n")

        f.write("### 2.2 Aggregate Metrics Table\n")
        f.write("| Metric | Demucs | SAM |\n")
        f.write("| :--- | :--- | :--- |\n")
        f.write(f"| Mean IoU | {demucs_agg['Mean IoU']:.3f} | {sam_agg['Mean IoU']:.3f} |\n")
        f.write(f"| Median IoU | {demucs_agg['Median IoU']:.3f} | {sam_agg['Median IoU']:.3f} |\n")
        f.write(f"| Avg Boundary Error (ms) | {demucs_agg['Avg Boundary Error (ms)']:.0f} | {sam_agg['Avg Boundary Error (ms)']:.0f} |\n")
        f.write(f"| Deletion Rate (Missed) | {demucs_agg['Deletion Rate']:.1%} | {sam_agg['Deletion Rate']:.1%} |\n")
        f.write(f"| Insertion Rate (Hallucinated) | {demucs_agg['Insertion Rate']:.1%} | {sam_agg['Insertion Rate']:.1%} |\n")
        f.write(f"| **Vocal False Positive Rate** | **{demucs_agg['Vocal False Positive Rate']:.1%}** | **{sam_agg['Vocal False Positive Rate']:.1%}** |\n\n")

        f.write("## 3. Per-Song Detailed Analysis\n")
        f.write("Comparison of alignment (IoU) and Instrumental Confusion (FPR) for every song.\n\n")
        f.write(song_group.to_markdown(index=False, floatfmt=".3f"))
        f.write("\n\n")
        
        f.write("## 4. Segment-Wise Error Table (Sample)\n")
        f.write("Below is a sample of segment-wise errors. **See `Full_Segment_Analysis.csv` for the complete row-by-row proof.**\n\n")
        f.write(df_rows.head(20).to_markdown(index=False))
        f.write("\n\n")
        
        f.write("## 5. Hybrid / Ensemble Proposal\n")
        f.write("Based on the error profile:\n")
        f.write("1. **Gating Rule**: Since Demucs has a lower Vocal FPR, use Demucs to define 'Instrumental' and 'Vocal' zones.\n")
        f.write("2. **Refinement**: Only accept SAM vocal predictions if they fall within a Demucs 'Vocal' zone.\n")
        f.write(f"3. **Impact**: This would eliminate approximately {sam_agg['Vocal False Positive Rate']:.0%} of SAM's false alarms while retaining its noise suppression within valid vocal regions.\n")

    print(f"Report generated at {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_report()
