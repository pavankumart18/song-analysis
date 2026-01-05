import shutil
from pathlib import Path
import os

def separate_folders():
    songs_to_process = [
        "ghallu_ghallu",
        "Mari_Antaga_SVSC_Movie",
        "Naa_Autograph_Sweet_Memories",
        "Narasimha_-_Narasimha",
        "Narasimha_Yekku_Tholi_Mettu",
        "Oh_Sita_Hey_Rama",
        "Pilichina_Ranantava_Song_With",
        "Raja_Edo_Oka_Ragam"
    ]
    
    base_dir = Path(".")
    
    for song_name in songs_to_process:
        original_path = base_dir / song_name
        
        if not original_path.exists():
            print(f"[Skip] {song_name} not found.")
            continue
            
        print(f"Processing {song_name}...")
        
        # Define new paths
        sam_path = base_dir / f"{song_name}_SAM"
        demucs_path = base_dir / f"{song_name}_Demucs"
        
        # 1. Rename Original -> SAM
        # If SAM already exists, assume we already did this or handle collision
        if not sam_path.exists():
            try:
                original_path.rename(sam_path)
                print(f"  Renamed to {sam_path.name}")
            except Exception as e:
                print(f"  [Error] Renaming failed: {e}")
                continue
        else:
            print(f"  {sam_path.name} already exists. checking original.")
            if original_path.exists():
                # If both exist, maybe we just didn't finish the rest?
                # We'll treat original as source for Demucs if needed, but logic is tricky.
                # Let's assume clear slate: renaming original is key.
                pass
        
        # 2. Create Demucs folder
        if not demucs_path.exists():
            demucs_path.mkdir()
            print(f"  Created {demucs_path.name}")
            
            # 3. Copy song.mp3 to Demucs folder
            # Source is now sam_path (since we renamed original)
            src_audio = sam_path / "song.mp3"
            dst_audio = demucs_path / "song.mp3"
            
            if src_audio.exists():
                shutil.copy2(src_audio, dst_audio)
                print("  Copied song.mp3 to Demucs folder")
            else:
                print("  [Warning] song.mp3 not found in SAM folder!")

if __name__ == "__main__":
    separate_folders()
