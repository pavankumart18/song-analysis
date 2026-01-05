import os
import shutil
from pathlib import Path

def cleanup_duplicates():
    base_path = Path(r"c:\Users\admin\Desktop\song analysis\data")
    if not base_path.exists():
        print("Data dir not found")
        return

    # Group folders by song name prefix
    # Naming convention: {Name}_{Type}
    # We want to keep song.mp3 in Manual, delete in others.
    
    deleted_count = 0
    saved_space = 0
    
    # scan for directories
    dirs = [d for d in base_path.iterdir() if d.is_dir()]
    
    # Map song_base_name -> { 'Manual': path, 'Demucs': path, 'SAM': path }
    song_groups = {}
    
    for d in dirs:
        name = d.name
        if name.endswith("_Manual"):
            base = name[:-7]
            type_ = "Manual"
        elif name.endswith("_Demucs"):
            base = name[:-7]
            type_ = "Demucs"
        elif name.endswith("_SAM"):
            base = name[:-4]
            type_ = "SAM"
        else:
            continue
            
        if base not in song_groups:
            song_groups[base] = {}
        song_groups[base][type_] = d

    for base, variants in song_groups.items():
        # Determine the "Master" folder (Manual preferentially)
        master_folder = variants.get("Manual")
        if not master_folder:
            # Fallback to Demucs, then SAM
            master_folder = variants.get("Demucs")
        if not master_folder:
            master_folder = variants.get("SAM")
            
        if not master_folder:
            continue
            
        print(f"Processing group: {base} (Master: {master_folder.name})")
        
        # Ensure Master has the song
        master_song = master_folder / "song.mp3"
        if not master_song.exists():
             # Try to move from another variant if master is missing it
             for v_type, v_path in variants.items():
                 cand = v_path / "song.mp3"
                 if cand.exists():
                     print(f"  Moving song.mp3 from {v_type} to Master...")
                     shutil.move(str(cand), str(master_song))
                     break
        
        # Now delete duplicates in others
        for v_type, v_path in variants.items():
            if v_path == master_folder:
                continue
                
            dup_song = v_path / "song.mp3"
            if dup_song.exists():
                size = dup_song.stat().st_size
                print(f"  Deleting duplicate in {v_type} ({size/1024/1024:.2f} MB)")
                os.remove(dup_song)
                deleted_count += 1
                saved_space += size
                
            # Also clean wavs if any remain
            dup_wav = v_path / "song.wav"
            if dup_wav.exists():
                os.remove(dup_wav)

    print(f"Cleanup complete. Deleted {deleted_count} files. Saved {saved_space/1024/1024:.2f} MB.")

if __name__ == "__main__":
    cleanup_duplicates()
