import os
import json
import glob
from pathlib import Path
import requests

# Configuration
API_URL = "https://llmfoundry.straive.com/openai/v1/chat/completions"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRwYXZhbi5rdW1hckBncmFtZW5lci5jb20ifQ.dIjgC3eykiiux4vJW0HvpARLLgjAoVFgU5XJIfZ94hY"
BASE_DIR = r"c:\Users\admin\Desktop\song analysis\data"

def get_demucs_sam_pairs(base_dir):
    """
    Finds matching Demucs, SAM, and Manual folders for each song.
    Returns dict: { "Song Name": { "Demucs": path, "SAM": path, "Manual": path } }
    """
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

def analyze_structure_file(json_path):
    """
    Extracts quantitative metrics from song_structure.json
    """
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        stats = {
            "total_segments": len(data),
            "vocal_segments": len([s for s in data if s.get('type') == 'vocals']),
            "avg_segment_duration": 0,
            "pallavi_detected": any(s.get('label') == 'Pallavi' for s in data),
            "interludes_detected": len([s for s in data if 'Interlude' in s.get('label', '')])
        }
        
        durations = [s['end'] - s['start'] for s in data]
        if durations:
            stats["avg_segment_duration"] = round(sum(durations) / len(durations), 2)
            
        return stats
    except:
        return None

def read_human_feedback(folder):
    """
    Reads human_analysis.md if present
    """
    try:
        # Search for any .md file with 'analysis'
        for f in folder.glob("*analysis*.md"): # Case insensitive globe usually requires pattern matching
             # simplified
             pass
        
        # Specific check
        candidates = list(folder.glob("*human_analysis.md")) + list(folder.glob("*Human_analysis.md")) + list(folder.glob("*Human_Analysis.md"))
        if candidates:
            with open(candidates[0], 'r', encoding='utf-8') as f:
                return f.read()
    except:
        pass
    return None

def generate_technical_report():
    pairs = get_demucs_sam_pairs(BASE_DIR)
    
    # 1. Aggregate Data
    aggregated_data = []
    
    for song, folders in pairs.items():
        entry = { "song": song, "demucs": {}, "sam": {}, "manual": {}, "comparison_notes": "" }
        
        # Demucs Stats
        if "Demucs" in folders:
            d_path = folders["Demucs"]
            entry["demucs"] = analyze_structure_file(d_path / "song_structure.json")
            # We assume human analysis is in the Demucs folder as per user workflow
            entry["comparison_notes"] = read_human_feedback(d_path)
            
        # SAM Stats
        if "SAM" in folders:
            s_path = folders["SAM"]
            entry["sam"] = analyze_structure_file(s_path / "song_structure.json")

        # Manual Stats
        if "Manual" in folders:
             m_path = folders["Manual"]
             entry["manual"] = analyze_structure_file(m_path / "song_structure.json")
            
        aggregated_data.append(entry)

    print(f"Aggregated data for {len(aggregated_data)} songs: {[e['song'] for e in aggregated_data]}")

    # 2. LLM Generation
    system_prompt = """
    You are a Lead Audio Engineer generating a Formal Technical Audit Report.
    
    **Objective**: Evaluate the performance of "Demucs" vs "SAM" for Indian Source Separation & Segmentation, using "Manual" separation as the Ground Truth.
    
    **Input Data**:
    A JSON list containing:
    - Quantitative Metrics (Segment counts, detection of Pallavi/Interludes) for Demucs, SAM, and Manual text.
    - Qualitative Notes (Human Analysis) describing specific failures (e.g. "Violin confusion").
    
    **Report Requirements**:
    Create a professional "Technical Assessment Report" (Markdown) with the following sections:
    
    1. **Executive Summary**: 
       - High-level conclusion. Compare AI models (Demucs, SAM) against the Manual Ground Truth. 
       - (e.g. "Demucs offers superior stability closest to Manual segmentation, while SAM excels in noise suppression but suffers from instrumental confusion.")
    
    2. **Methodology Overview**:
       - Briefly describe the comparison framework (Waveform vs Spectrogram Masking) and the use of Manual segmentation as the baseline.
    
    3. **Quantitative Performance Metrics**:
       - Create a Markdown Table comparing key stats across the dataset for Demucs, SAM, and Manual.
       - **CRITICAL: You MUST include ALL songs provided in the input data in this table. Do not summarize or truncate the list.**
       - Include columns for "Manual (GT)", "Demucs", and "SAM".
       - Highlight discrepancies (e.g. Does SAM consistently under-segment compared to Manual?).
    
    4. **Qualitative Error Analysis (Thematic)**:
       - **Spectral Confusion**: Analyze the "Violin/Flute" issue reported in the notes.
       - **VAD Sensitivity**: Analyze the "Noise vs Vocals" trade-off.
       - **Structural Integrity**: Discuss how faithfully the models capture the Manual structure (Pallavi/Charanam).
    
    5. **Song-Specific Technical Audit**:
       - For 3-4 key examples (e.g. Ghallu Ghallu, Robo, Nuvvostanante), provide a mini-audit:
         - Compare the number of segments found by Demucs/SAM vs Manual.
         - *Issue*: What broke?
         - *Root Cause*: (e.g. Model Size, Training Data bias).
         - *Impact*: Critical/Minor.
    
    6. **Recommendations**:
       - Final technical recommendation for the production pipeline based on proximity to Manual quality.
    
    **Tone**: Formal, Objective, Engineering-focused. Avoid "storytelling". Use terms like "Signal-to-Noise Ratio", "False Positives", "Harmonic content", "Ground Truth".
    """
    
    user_payload = json.dumps(aggregated_data, indent=2)
    
    payload = {
        "model": "gpt-4o", 
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_payload}
        ],
        "temperature": 0.2
    }
    
    print("Generating Formal Report...")
    try:
        resp = requests.post(API_URL, headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}, json=payload, timeout=120)
        resp.raise_for_status()
        report = resp.json()["choices"][0]["message"]["content"]
        
        out_path = Path(BASE_DIR).parent / "Technical_Assessment_Report.md"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(report)
            
        print(f"Report generated: {out_path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_technical_report()
