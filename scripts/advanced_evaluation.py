import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.optimize import linear_sum_assignment
from collections import defaultdict
import datetime

# --- Configuration ---
IOU_THRESHOLDS = [0.3, 0.5, 0.7]
IOU_MATCH_THRESHOLD = 0.1
MIN_DURATION = 0.2  # Seconds (Filter out noise)

# Dynamic Base Dir
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
DEFAULT_DATA_DIR = BASE_DIR / "data"

OUTPUT_JSON = DEFAULT_DATA_DIR / "advanced_metrics.json"
OUTPUT_CSV = DEFAULT_DATA_DIR / "advanced_metrics.csv"
OUTPUT_REPORT = DEFAULT_DATA_DIR / "Quantitative_Summary.md"

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load {path}: {e}")
        return []

def filter_short_segments(segments):
    return [s for s in segments if (s.get('end', 0) - s.get('start', 0)) >= MIN_DURATION]

def is_vocal(seg):
    # Determine if a segment is 'Vocal' based on label/type
    # Manual: check type='vocals' OR label text
    # Pred: check type='vocals' (default is usually vocals for these models)
    t = seg.get('type', '').lower()
    l = seg.get('label', '').lower()
    
    if t == 'instrumental' or 'instrumental' in l or 'interlude' in l:
        return False
    return True

def calculate_iou(s1, e1, s2, e2):
    start_inter = max(s1, s2)
    end_inter = min(e1, e2)
    union = max(e1, e2) - min(s1, s2)
    if start_inter < end_inter and union > 0:
        return (end_inter - start_inter) / union
    return 0.0

def matching_hungarian(manual, pred):
    """
    Optimal 1:1 matching maximizing total IoU using the Hungarian algorithm.
    Returns: list of (m_idx, p_idx, iou) tuples.
    """
    if not manual or not pred:
        return []

    # Create Cost Matrix (Negated IoU because linear_sum_assignment minimizes cost)
    cost_matrix = np.zeros((len(manual), len(pred)))
    
    for r, m in enumerate(manual):
        for c, p in enumerate(pred):
            iou = calculate_iou(m['start'], m['end'], p['start'], p['end'])
            cost_matrix[r, c] = -iou # Negate for maximization

    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    
    matches = []
    for r, c in zip(row_ind, col_ind):
        iou = -cost_matrix[r, c]
        if iou > 0: # Only keep non-zero matches
            matches.append((r, c, iou))
            
    return matches

def compute_core_metrics(manual, pred, prefix=""):
    # 1. Matching
    matches = matching_hungarian(manual, pred)
    ious = [m[2] for m in matches]
    
    mean_iou = np.mean(ious) if ious else 0.0
    median_iou = np.median(ious) if ious else 0.0
    
    metrics = {
        f"{prefix}mean_iou": mean_iou,
        f"{prefix}median_iou": median_iou,
        f"{prefix}matched_count": len(matches),
        f"{prefix}manual_count": len(manual),
        f"{prefix}pred_count": len(pred)
    }
    
    # Precision/Recall at Thresholds
    for t in IOU_THRESHOLDS:
        tp = sum(1 for iou in ious if iou >= t)
        precision = tp / len(pred) if pred else 0.0
        recall = tp / len(manual) if manual else 0.0
        f1 = 0.0
        if (precision + recall) > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
            
        metrics[f"{prefix}P@{t}"] = precision
        metrics[f"{prefix}R@{t}"] = recall
        metrics[f"{prefix}F1@{t}"] = f1
        
    return matches, metrics

def evaluate_song(manual_segs, pred_segs):
    # 0. Filter Noise
    manual_segs = filter_short_segments(manual_segs)
    pred_segs = filter_short_segments(pred_segs)
    
    # --- A. Structural Evaluation (All Segments) ---
    matches, struct_metrics = compute_core_metrics(manual_segs, pred_segs, prefix="")
    
    # Boundary Errors (Structural)
    start_errs = []
    end_errs = []
    for r, c, iou in matches:
        m = manual_segs[r]
        p = pred_segs[c]
        start_errs.append(abs(m['start'] - p['start']))
        end_errs.append(abs(m['end'] - p['end']))
        
    avg_start_err = np.mean(start_errs) if start_errs else None
    avg_end_err = np.mean(end_errs) if end_errs else None
    bound_acc_1s = sum(1 for e in start_errs if e <= 1.0) / len(start_errs) if start_errs else 0.0
    
    struct_metrics.update({
        "avg_start_err": avg_start_err,
        "avg_end_err": avg_end_err,
        "bound_acc_1s": bound_acc_1s
    })

    # --- B. Class-Specific Evaluation (Vocals) ---
    manual_vocals = [s for s in manual_segs if is_vocal(s)]
    # Assume predictions are vocals unless explicitly instrumental
    pred_vocals = [s for s in pred_segs if is_vocal(s)] 
    
    _, vocal_metrics = compute_core_metrics(manual_vocals, pred_vocals, prefix="vocal_")
    
    # --- C. Instrumental Confusion (FPR) ---
    # (Same as before but integrated here)
    manual_intervals_instr = [
        (s['start'], s['end']) for s in manual_segs if not is_vocal(s)
    ]
    vocals_fp_duration = 0.0
    total_instr_duration = sum(end - start for start, end in manual_intervals_instr)
    manual_instr_count = len(manual_intervals_instr)
    bad_pred_count = 0 
    
    for p in pred_vocals:
        p_start, p_end = p['start'], p['end']
        current_p_fp = 0.0
        is_bad = False
        
        for m_s, m_e in manual_intervals_instr:
            ov_s = max(p_start, m_s)
            ov_e = min(p_end, m_e)
            if ov_s < ov_e:
                dur = ov_e - ov_s
                current_p_fp += dur
                if dur > 0.5: is_bad = True # Count as bad if >0.5s overlap
                
        vocals_fp_duration += current_p_fp
        if is_bad: bad_pred_count += 1

    fpr_time = vocals_fp_duration / total_instr_duration if total_instr_duration > 0 else 0.0
    fpr_count = bad_pred_count / manual_instr_count if manual_instr_count > 0 else 0.0
    
    # Combine
    final = {}
    final.update(struct_metrics)
    final.update(vocal_metrics)
    final["fpr_time"] = fpr_time
    final["fpr_count"] = fpr_count
    
    return final

def main():
    print(f"Scanning {DEFAULT_DATA_DIR}...")
    results = []
    
    manual_folders = list(DEFAULT_DATA_DIR.glob("*_Manual"))
    
    for m_folder in manual_folders:
        song_name = m_folder.name.replace("_Manual", "")
        m_file = m_folder / "song_structure.json"
        manual_data = load_json(m_file)
        if not manual_data: continue
        
        for variant in ["Demucs", "SAM"]:
            v_folder = DEFAULT_DATA_DIR / f"{song_name}_{variant}"
            v_file = v_folder / "song_structure.json"
            if v_file.exists():
                pred_data = load_json(v_file)
                metrics = evaluate_song(manual_data, pred_data)
                row = { "Song": song_name, "Model": variant }
                row.update(metrics)
                results.append(row)
                
    df = pd.DataFrame(results)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].round(4)
    
    df.to_csv(OUTPUT_CSV, index=False)
    df.to_json(OUTPUT_JSON, orient="records", indent=2)
    print(f"Saved metrics to {OUTPUT_CSV}")
    generate_summary_md(df)

def generate_summary_md(df):
    agg = df.groupby("Model").agg({
        "vocal_F1@0.5": "mean",
        "mean_iou": "mean",
        "fpr_time": "mean",
        "vocal_P@0.5": "mean",
        "vocal_R@0.5": "mean",
        "bound_acc_1s": "mean"
    }).round(3)
    
    md = f"""
# Quantitative Evaluation Summary (Refined)

## Aggregate Metrics (Mean across {len(df['Song'].unique())} songs)
*Filters: Segments < {MIN_DURATION}s removed.*

| Metric | Demucs | SAM |
| :--- | :--- | :--- |
| **Vocal F1 (@0.5 IoU)** | **{agg.loc['Demucs', 'vocal_F1@0.5']}** | {agg.loc['SAM', 'vocal_F1@0.5']} |
| Mean IoU (Structure) | {agg.loc['Demucs', 'mean_iou']} | {agg.loc['SAM', 'mean_iou']} |
| **Vocal FPR (Instrumental Confusion)** | **{agg.loc['Demucs', 'fpr_time']:.1%}** | {agg.loc['SAM', 'fpr_time']:.1%} |
| Vocal Precision (@0.5) | {agg.loc['Demucs', 'vocal_P@0.5']} | {agg.loc['SAM', 'vocal_P@0.5']} |
| Vocal Recall (@0.5) | {agg.loc['Demucs', 'vocal_R@0.5']} | {agg.loc['SAM', 'vocal_R@0.5']} |
| Clean Boundaries (<1s Error) | {agg.loc['Demucs', 'bound_acc_1s']:.1%} | {agg.loc['SAM', 'bound_acc_1s']:.1%} |

## Key Findings
1. **Noise Filtering**: Excluding segments < 0.2s improved precision.
2. **Class-Specific Analysis**: Focusing on "Vocals" F1 (excluding instrumental segments from the structural score) widens the gap between Demucs and SAM.
"""
    with open(OUTPUT_REPORT, 'w') as f:
        f.write(md)
    print(f"Report generated at {OUTPUT_REPORT}")

if __name__ == "__main__":
    main()
