import shutil
from pathlib import Path

def split_new_songs():
    songs_to_process = [
        "Nuvvostanante_Nenoddantana_s",
        "robo"
    ]
    
    base_dir = Path(".")
    
    for song_name in songs_to_process:
        original_path = base_dir / song_name
        
        # Define new paths
        sam_path = base_dir / f"{song_name}_SAM"
        demucs_path = base_dir / f"{song_name}_Demucs"
        
        if sam_path.exists():
            print(f"[Skip] {sam_path.name} already exists.")
            continue
            
        if not original_path.exists():
            print(f"[Skip] {song_name} not found.")
            continue
            
        print(f"Processing {song_name}...")
        
        # 1. Rename Original -> SAM
        try:
            original_path.rename(sam_path)
            print(f"  Renamed to {sam_path.name}")
        except Exception as e:
            print(f"  [Error] Renaming failed: {e}")
            continue
        
        # 2. Create Demucs folder
        if not demucs_path.exists():
            demucs_path.mkdir()
            print(f"  Created {demucs_path.name}")
            
            # 3. Copy song.mp3 to Demucs folder
            src_audio = sam_path / "song.mp3"
            dst_audio = demucs_path / "song.mp3"
            
            if src_audio.exists():
                shutil.copy2(src_audio, dst_audio)
                print("  Copied song.mp3 to Demucs folder")
            else:
                print("  [Warning] song.mp3 not found in SAM folder!")

if __name__ == "__main__":
    split_new_songs()
