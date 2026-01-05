from pathlib import Path
import json
from audio_slicer import AudioSlicer
from player_generator import PlayerGenerator

def process_manual_folders():
    base_dir = Path(".")
    
    # Find all manual folders
    manual_folders = [d for d in base_dir.iterdir() if d.is_dir() and d.name.endswith("_Manual")]
    
    slicer = AudioSlicer()
    player_gen = PlayerGenerator()
    
    for folder in manual_folders:
        print(f"\nProcessing {folder.name}...")
        
        song_file = folder / "song.mp3"
        structure_file = folder / "song_structure.json"
        
        if not song_file.exists():
            print(f"  [Error] song.mp3 not found in {folder.name}")
            continue
            
        if not structure_file.exists():
            print(f"  [Error] song_structure.json not found in {folder.name}")
            continue
            
        # Load structure
        try:
            with open(structure_file, 'r', encoding='utf-8') as f:
                structure = json.load(f)
        except Exception as e:
            print(f"  [Error] Failed to load json: {e}")
            continue
            
        # 1. Slice Audio
        try:
            print("  Slicing info segments...")
            # We use the existing AudioSlicer logic. 
            # It creates a 'segmented_parts' folder inside the song folder.
            merged_file = slicer.slice_and_merge(song_file, structure)
            print(f"  Separated audio stored in {folder.name}/segmented_parts")
        except Exception as e:
            print(f"  [Error] Slicing failed: {e}")
            
        # 2. Generate Player
        try:
            print("  Generating Player...")
            # We pass None for lyrics_data as manual structure json currently doesn't have lyrics text mapped per block
            # (The MD has lyrics, but we only parsed timestamps into the json)
            player_gen.generate(song_file, structure_file, lyrics_data=None) 
            print("  Player generated.")
        except Exception as e:
             print(f"  [Error] Player generation failed: {e}")

if __name__ == "__main__":
    process_manual_folders()
