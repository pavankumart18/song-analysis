from pathlib import Path
from main import process_song

def run_all_analysis():
    base_dir = Path(".")
    
    # Find all Demucs and SAM folders
    all_folders = [d for d in base_dir.iterdir() if d.is_dir() and (d.name.endswith("_Demucs") or d.name.endswith("_SAM"))]
    
    # Sort for consistent order
    all_folders.sort(key=lambda x: x.name)
    
    print(f"Found {len(all_folders)} folders to process.")
    
    for folder in all_folders:
        song_file = folder / "song.mp3"
        
        if song_file.exists():
            print(f"\n[Batch] Starting extensive analysis for: {folder.name}")
            try:
                # process_song handles separation (skips if done) and analysis (re-runs due to our edit)
                process_song(song_file)
            except Exception as e:
                print(f"[Batch] Failed to process {folder.name}: {e}")
        else:
            print(f"[Batch] Warning: song.mp3 not found in {folder.name}")

if __name__ == "__main__":
    run_all_analysis()
