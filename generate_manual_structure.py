import re
import json
from pathlib import Path

def parse_timestamps(text):
    """
    Parses "mm:ss - mm:ss - Label" lines into blocks.
    """
    blocks = []
    
    # Regex to capture "0:00 - 0:10 - Label" format
    # Supports variations like optional spaces, different separators
    pattern = r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})\s*[-–]\s*(.*)'
    
    for line in text.splitlines():
        line = line.strip()
        if not line: continue
        
        match = re.search(pattern, line)
        if match:
            start_str, end_str, label = match.groups()
            
            # Convert mm:ss to seconds
            def to_sec(t_str):
                m, s = map(int, t_str.split(':'))
                return m * 60 + s
            
            start = to_sec(start_str)
            end = to_sec(end_str)
            
            # Determine type (vocals vs instrumental) based on label
            label_lower = label.lower()
            block_type = "vocals"
            if "instrumental" in label_lower or "interlude" in label_lower or "intro" in label_lower or "outro" in label_lower:
                # Unless it says "humming" which is usually vocal, but user marked some intros as standard blocks.
                # User marked "Intro (Instrumental )", "Interlude 1 ( Instrumental )".
                # But also "Humming" which is technically vocal.
                # Let's trust the label for visualization.
                if "humming" in label_lower:
                    block_type = "vocals"
                else:
                    block_type = "instrumental"
            
            blocks.append({
                "label": label.strip(),
                "start": float(start),
                "end": float(end),
                "type": block_type
            })
            
    return blocks

def generate_manual_structure_json():
    base_dir = Path(".")
    
    # Iterate over all _Manual folders
    manual_folders = [d for d in base_dir.iterdir() if d.is_dir() and d.name.endswith("_Manual")]
    
    for folder in manual_folders:
        md_file = folder / "Manual_Analysis.md"
        if not md_file.exists():
            continue
            
        print(f"Parsing structure for {folder.name}...")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract the "Manual Separation" section
        # We look for "# Manual Separation" and take everything after it until end or next header
        separation_match = re.search(r'# Manual Separation\s*(.*)', content, re.DOTALL)
        
        if separation_match:
            separation_text = separation_match.group(1)
            blocks = parse_timestamps(separation_text)
            
            if blocks:
                output_json = folder / "song_structure.json"
                with open(output_json, 'w') as f:
                    json.dump(blocks, f, indent=4)
                print(f"  Saved song_structure.json ({len(blocks)} blocks)")
                
                # Also generate CSV for consistency
                output_csv = folder / "song_structure.csv"
                with open(output_csv, 'w') as f:
                    f.write("start,end,label,type\n")
                    for b in blocks:
                        f.write(f"{b['start']},{b['end']},{b['label']},{b['type']}\n")
                print("  Saved song_structure.csv")
            else:
                print(f"  [Warning] No timestamp blocks found in {folder.name}")
        else:
             print(f"  [Warning] 'Manual Separation' section not found in {md_file.name}")

if __name__ == "__main__":
    generate_manual_structure_json()
