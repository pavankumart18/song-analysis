from pathlib import Path
from main import process_song

def run_batch_sam_new():
    songs_to_process = [
        "Nuvvostanante_Nenoddantana_s_SAM",
        "robo_SAM"
    ]
    
    base_dir = Path(".")
    
    for song_folder in songs_to_process:
        folder_path = base_dir / song_folder
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
    run_batch_sam_new()
