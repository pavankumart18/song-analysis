import re
from pathlib import Path
import shutil

def parse_manual_separation(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by songs using the header explicitly provided in the file
    # We look for "Manual Separation of " or "Next Song :"
    # But wait, looking at the file:
    # First song: "Manual Separation of Ghallu Ghallu"
    # Others: "Next Song : Mari Antaga SVSC Movie"
    
    # Let's split by "# Next Song :" for the later ones, and handle the first one specially.
    # Actually, we can just split by regex `# Next Song : (.*)` and also handle the first one.
    
    sections = re.split(r'# Next Song : ', content)
    
    parsed_songs = []
    
    # First section contains "Manual Separation of Ghallu Ghallu" (or broadly the first song)
    if sections:
        first_section = sections[0]
        # Try to find song name in first line
        match = re.search(r'# Manual Separation of (.*)', first_section)
        if match:
             song_name = match.group(1).strip()
             parsed_songs.append((song_name, first_section))
    
    # Subsequent sections have the song name as the first line (due to split)
    for section in sections[1:]:
        lines = section.split('\n')
        song_name = lines[0].strip()
        parsed_songs.append((song_name, section))
        
    return parsed_songs

def process_manual_data():
    base_dir = Path(".")
    md_file = base_dir / "Manual_Separated.MD"
    
    if not md_file.exists():
        print("Manual_Separated.MD not found!")
        return

    parsed_songs = parse_manual_separation(md_file)
    print(f"Found {len(parsed_songs)} songs in the manual file.")

    for song_name_raw, content in parsed_songs:
        # Determine the target internal folder name. The song names in MD might differ slightly (spaces vs underscores).
        # We need to match "Ghallu Ghallu" to "ghallu_ghallu" or similar.
        
        # Mapping Logic:
        # 1. Normalize both to lowercase, no spaces.
        # 2. Check if normalized version is substring of existing folder name.
        
        # Heuristic mapping for current project folders
        song_map = {
            "Ghallu Ghallu": "ghallu_ghallu",
            "Mari Antaga SVSC Movie": "Mari_Antaga_SVSC_Movie",
            "Naa Autograph Sweet Memories": "Naa_Autograph_Sweet_Memories",
            "Narasimha - Narasimha": "Narasimha_-_Narasimha",
            "Narasimha Yekku Tholi Mettu": "Narasimha_Yekku_Tholi_Mettu",
            "Oh Sita Hey Rama": "Oh_Sita_Hey_Rama",
            "Pilichina Ranantava Song With": "Pilichina_Ranantava_Song_With",
            "Raja Edo Oka Ragam": "Raja_Edo_Oka_Ragam",
            "Robo": "robo",
            "Nuvvostanante Nenoddantana": "Nuvvostanante_Nenoddantana_s"
        }
        
        target_folder = song_map.get(song_name_raw.strip())
        
        if not target_folder:
            print(f"Could not map '{song_name_raw}' to a valid folder. Skipping.")
            continue
            
        print(f"Processing {song_name_raw} -> {target_folder}...")
        
        # Create _Manual folder
        new_folder_name = f"{target_folder}_Manual"
        new_folder_path = base_dir / new_folder_name
        
        if not new_folder_path.exists():
            new_folder_path.mkdir()
            print(f"  Created {new_folder_name}")
        
        # 1. Copy song.mp3 from an existing source (e.g., _Demucs or _SAM or original)
        # We try finding song.mp3 in the _Demucs folder first
        demucs_path = base_dir / f"{target_folder}_Demucs"
        src_audio = demucs_path / "song.mp3"
        dst_audio = new_folder_path / "song.mp3"
        
        if not src_audio.exists():
             # Fallback to SAM path
            sam_path = base_dir / f"{target_folder}_SAM"
            src_audio = sam_path / "song.mp3"
            
        if src_audio.exists():
            if not dst_audio.exists():
                shutil.copy2(src_audio, dst_audio)
                print("  Copied song.mp3")
        else:
            print(f"  [Warning] song.mp3 not found for {target_folder}")

        # 2. Save the extracted MD content to "Manual_Analysis.md"
        output_md_path = new_folder_path / "Manual_Analysis.md"
        with open(output_md_path, 'w', encoding='utf-8') as f:
            f.write(f"# Manual Analysis for {song_name_raw}\n\n{content}")
        print("  Saved Manual_Analysis.md")

if __name__ == "__main__":
    process_manual_data()
