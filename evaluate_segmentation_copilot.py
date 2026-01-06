#!/usr/bin/env python3
"""
evaluate_segmentation_copilot.py

Usage:
    python evaluate_segmentation_copilot.py --data-dir data --out metrics_copilot.csv

This scans folders in data/ that end with _Manual and expects corresponding
_SAM and _Demucs folders with song_structure.json files. It computes:
 - mean IoU between predicted segments and manual segments (greedy matching)
 - precision/recall/F1 at IoU threshold (default 0.5)
 - mean boundary error (start/end) for matched segments
 - counts: #manual segments, #pred_segments

Outputs: metrics.csv and metrics.json (per-song + aggregated).
"""
import json
from pathlib import Path
from collections import defaultdict
import argparse
import csv
import math

# Use the correct data directory for the user's setup
DEFAULT_DATA_DIR = r"c:\Users\admin\Desktop\song analysis\data"

def load_structure(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return []

def iou_interval(a_start, a_end, b_start, b_end):
    inter = max(0.0, min(a_end, b_end) - max(a_start, b_start))
    union = max(a_end, b_end) - min(a_start, b_start)
    if union <= 0: return 0.0
    return inter / union

def match_greedy(manual, pred):
    """Greedy matching by highest IoU pairs; returns list of matches (m_idx, p_idx, iou)."""
    matches = []
    used_m = set()
    used_p = set()
    # build all IoUs
    ious = []
    for mi, m in enumerate(manual):
        for pi, p in enumerate(pred):
            i = iou_interval(m['start'], m['end'], p['start'], p['end'])
            ious.append((i, mi, pi))
    ious.sort(reverse=True, key=lambda x: x[0])
    for i, mi, pi in ious:
        if i <= 0: break
        if mi in used_m or pi in used_p: continue
        used_m.add(mi); used_p.add(pi)
        matches.append((mi, pi, i))
    return matches

def boundary_errors(manual_block, pred_block):
    start_err = abs(manual_block['start'] - pred_block['start'])
    end_err = abs(manual_block['end'] - pred_block['end'])
    return start_err, end_err

def evaluate_pair(manual, pred, iou_threshold=0.5):
    matches = match_greedy(manual, pred)
    # metrics
    iou_vals = [i for (_,_,i) in matches]
    mean_iou = sum(iou_vals)/len(iou_vals) if iou_vals else 0.0
    # precision: proportion of predicted segments that are matched at IoU>=threshold
    tp = sum(1 for (_,_,i) in matches if i >= iou_threshold)
    precision = tp / len(pred) if pred else 0.0
    recall = tp / len(manual) if manual else 0.0
    f1 = 2*precision*recall/(precision+recall) if (precision+recall)>0 else 0.0
    # boundary errors for matched segments (use IoU>=0 to include all matched)
    start_errs = []
    end_errs = []
    for mi, pi, i in matches:
        se, ee = boundary_errors(manual[mi], pred[pi])
        start_errs.append(se); end_errs.append(ee)
    mean_start_err = sum(start_errs)/len(start_errs) if start_errs else None
    mean_end_err = sum(end_errs)/len(end_errs) if end_errs else None
    return {
        "mean_iou": mean_iou,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "mean_start_error": mean_start_err,
        "mean_end_error": mean_end_err,
        "manual_count": len(manual),
        "pred_count": len(pred),
        "matched_count": len(matches)
    }

def discover_songs(data_dir):
    d = Path(data_dir)
    manual_folders = [p for p in d.iterdir() if p.is_dir() and p.name.endswith("_Manual")]
    return manual_folders

def main(args):
    manual_folders = discover_songs(args.data_dir)
    results = []
    count = 0
    
    print(f"Scanning data dir: {args.data_dir}")
    
    for folder in manual_folders:
        song_root = folder.name.replace("_Manual","")
        manual_json = folder / "song_structure.json"
        
        # Check parent folder and current folder for siblings
        # Structure is usually: data/song_Manual, data/song_SAM
        parent_dir = folder.parent
        sam_json = parent_dir / f"{song_root}_SAM" / "song_structure.json"
        demucs_json = parent_dir / f"{song_root}_Demucs" / "song_structure.json"

        if not manual_json.exists():
            print(f"[WARN] manual structure missing: {manual_json}")
            continue

        manual = load_structure(manual_json)
        entry = {"song": song_root}
        # evaluate each model if present
        for model_name, path in (("SAM", sam_json), ("Demucs", demucs_json)):
            if path.exists():
                pred = load_structure(path)
                stats = evaluate_pair(manual, pred, iou_threshold=args.iou)
                # prefix keys
                for k,v in stats.items():
                    entry[f"{model_name.lower()}_{k}"] = v
            else:
                print(f"[INFO] {model_name} structure missing for {song_root} at {path}")
        results.append(entry)
        count += 1

    # write CSV
    out_csv = Path(args.out).with_suffix('.csv')
    if not results:
        print("No songs processed! Check data directory.")
        return

    keys = sorted({k for e in results for k in e.keys()})
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for e in results:
            w.writerow(e)
            
    # write JSON
    out_json = Path(args.out).with_suffix('.json')
    with open(out_json,'w',encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"Processed {count} songs. Metrics written to {out_csv} and {out_json}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    # Updated default path to be robust for the user's environment
    p.add_argument("--data-dir", default=DEFAULT_DATA_DIR, help="data folder containing song folders")
    p.add_argument("--out", default="data/copilot_metrics", help="base output path (without ext)")
    p.add_argument("--iou", type=float, default=0.5, help="IoU threshold for precision/recall")
    args = p.parse_args()
    main(args)
