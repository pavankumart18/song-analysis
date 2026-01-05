from pathlib import Path
from main import process_song

def run_batch_demucs():
    base_dir = Path(".")
    
    # Dynamically find all _Demucs folders
    demucs_folders = [d for d in base_dir.iterdir() if d.is_dir() and d.name.endswith("_Demucs")]
    
    for folder_path in demucs_folders:
        song_file = folder_path / "song.mp3"
        
        if song_file.exists():
            print(f"\n[Batch] Starting analysis for: {folder_path.name}")
            try:
                process_song(song_file)
            except Exception as e:
                print(f"[Batch] Failed to process {folder_path.name}: {e}")
        else:
            print(f"[Batch] Warning: {song_file} not found.")

if __name__ == "__main__":
    run_batch_demucs()
