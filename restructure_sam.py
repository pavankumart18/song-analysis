import shutil
from pathlib import Path
import os

def restructure_folders():
    # Current directory (song analysis root)
    base_dir = Path(".")
    
    # List of known folders provided by user context, or just discover them dynamically
    # Discovery is safer for "all relevant folders"
    
    count = 0
    for song_dir in base_dir.iterdir():
        if song_dir.is_dir():
            # Check for the presence of vocals.wav and no_vocals.wav at the root of the song dir
            vocab_path = song_dir / "vocals.wav"
            novocals_path = song_dir / "no_vocals.wav"
            
            # We operate if at least one of them exists to move it
            if vocab_path.exists() or novocals_path.exists():
                print(f"Processing {song_dir.name}...")
                
                # Target directory structure: separated/sam/song/
                # Note: User requested 'separated/sam/song/' specifically.
                target_dir = song_dir / "separated" / "sam" / "song"
                
                try:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    
                    if vocab_path.exists():
                        destination = target_dir / "vocals.wav"
                        shutil.move(str(vocab_path), str(destination))
                        print(f"  Moved vocals.wav -> {destination}")
                        
                    if novocals_path.exists():
                        destination = target_dir / "no_vocals.wav"
                        shutil.move(str(novocals_path), str(destination))
                        print(f"  Moved no_vocals.wav -> {destination}")
                        
                    count += 1
                except Exception as e:
                    print(f"  [Error] Failed to restructure {song_dir.name}: {e}")
            else:
                # folders that don't have these files (already processed or different structure)
                pass

    print(f"\nCompleted restructuring for {count} folders.")

if __name__ == "__main__":
    restructure_folders()
