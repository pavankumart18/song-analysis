import json
import os
from pathlib import Path

# Config
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_JSON = BASE_DIR / "quantitative_analysis.json"

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def calculate_iou(s1, e1, s2, e2):
    start_inter = max(s1, s2)
    end_inter = min(e1, e2)
    if start_inter < end_inter:
        intersection = end_inter - start_inter
        union = max(e1, e2) - min(s1, s2)
        return intersection / union if union > 0 else 0
    return 0

def analyze_song(song_name, manual_segments, predicted_segments):
    """
    Returns:
    {
        "metrics": { "mean_iou": float, "fpr": float },
        "segments": [ { "start": float, "end": float, "iou": float, "error_type": str } ]
    }
    """
    total_iou = 0
    ious = []
    enriched_segments = []
    
    # Identify instrumental sections in Manual for FPR calculation
    manual_instrumentals = [s for s in manual_segments if s.get('type') == 'instrumental']
    
    label_confusions = 0 # Instrumental in manual -> Vocal in prediction
    
    # We iterate through PREDICTED segments to score them
    for p_seg in predicted_segments:
        p_start, p_end = p_seg['start'], p_seg['end']
        p_type = p_seg.get('type', 'unknown').lower()
        
        # Find best matching manual segment
        best_iou = 0
        best_m_seg = None
        
        for m_seg in manual_segments:
            iou = calculate_iou(m_seg['start'], m_seg['end'], p_start, p_end)
            if iou > best_iou:
                best_iou = iou
                best_m_seg = m_seg
                
        # Determine Error Type
        error_type = None
        
        if best_iou < 0.1:
            error_type = "Hallucination"
        else:
            # Check confusion
            if best_m_seg:
                m_type = best_m_seg.get('type', 'unknown').lower()
                if m_type == 'instrumental' and p_type == 'vocals':
                    error_type = "Confusion"
                    label_confusions += 1
        
        enriched_segments.append({
            "start": p_start,
            "end": p_end,
            "iou": round(best_iou, 2),
            "error_type": error_type
        })
        ious.append(best_iou)

    # Calculate Metrics
    mean_iou = sum(ious) / len(ious) if ious else 0
    
    # FPR calculation: Segments that overlap significantly with Manual Instrumental and are labeled Vocal
    # A simplified FPR: Count of "Confusion" errors / Count of Manual Instrumental Segments
    fpr = 0
    if len(manual_instrumentals) > 0:
        fpr = label_confusions / len(manual_instrumentals)
        
    return {
        "metrics": {
            "mean_iou": round(mean_iou, 3),
            "fpr": round(fpr, 3)
        },
        "segments": enriched_segments
    }

def main():
    # 1. Group Paths
    grouped = {}
    for item in BASE_DIR.iterdir():
        if not item.is_dir(): continue
        
        key = None
        variant = None
        
        if item.name.endswith("_Manual"):
            key = item.name[:-7]
            variant = "Manual"
        elif item.name.endswith("_Demucs"):
            key = item.name[:-7]
            variant = "Demucs"
        elif item.name.endswith("_SAM"):
            key = item.name[:-4]
            variant = "SAM"
            
        if key:
            if key not in grouped: grouped[key] = {}
            grouped[key][variant] = item

    # 2. Analyze
    results = {}
    
    for song, folders in grouped.items():
        if "Manual" not in folders: continue
        
        manual_data = load_json(folders["Manual"] / "song_structure.json")
        results[song] = {}
        
        for variant in ["Demucs", "SAM"]:
            if variant in folders:
                pred_data = load_json(folders[variant] / "song_structure.json")
                analysis = analyze_song(song, manual_data, pred_data)
                results[song][variant] = analysis

    # 3. Save
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Analysis complete. Saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
