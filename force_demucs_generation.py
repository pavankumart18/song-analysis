import sys
import subprocess
from pathlib import Path

def run_demucs_force():
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
        audio_path = folder_path / "song.mp3"
        
        if not audio_path.exists():
            print(f"[Skip] {audio_path} not found.")
            continue
            
        print(f"\n=== Running Demucs for {song_folder} ===")
        
        output_dir = folder_path / "separated"
        
        # Using uv to run demucs as per previous project patterns
        # Note: --mp3 flag creates mp3s. If we want wavs (which pipeline expects often), we should omit --mp3 or check expectations.
        # DemucsRunner usually produces .wav by default.
        # process_folders.py had --mp3. main.py analysis often looks for .wav blocks.
        # However, DemucsRunner typically creates .wav.
        # I will stick to default (WAV) to match standard DemucsRunner behavior in this project.
        
        cmd = [
            sys.executable, "-m", "uv", "tool", "run",
            "--python", "3.10",
            "--with", "soundfile",
            "demucs",
            "-n", "htdemucs",
            "--two-stems", "vocals",
            "-o", str(output_dir),
            str(audio_path)
        ]
        
        try:
            # subprocess.run(cmd, check=True)
            # Using shell=False usually preferred, but sometimes path issues occur.
            proc = subprocess.run(cmd, check=True, capture_output=False) # let it print to stdout
            print(f"[Success] Demucs finished for {song_folder}")
        except subprocess.CalledProcessError as e:
            print(f"[Error] Demucs failed for {song_folder}: {e}")
        except Exception as e:
            print(f"[Error] Unexpected error for {song_folder}: {e}")

if __name__ == "__main__":
    run_demucs_force()
