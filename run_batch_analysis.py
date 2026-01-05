from pathlib import Path
from main import process_song

def run_batch():
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
    
    for song_folder in songs_to_process:
        folder_path = base_dir / song_folder
        song_file = folder_path / "song.mp3"
        
        if song_file.exists():
            print(f"\n[Batch] Starting analysis for: {song_folder}")
            try:
                process_song(song_file)
            except Exception as e:
                print(f"[Batch] Failed to process {song_folder}: {e}")
        else:
            print(f"[Batch] Warning: {song_file} not found.")

if __name__ == "__main__":
    run_batch()
