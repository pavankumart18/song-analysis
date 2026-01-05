import sys
import subprocess
from pathlib import Path

def run_demucs_new():
    songs_to_process = [
        "Nuvvostanante_Nenoddantana_s_Demucs",
        "robo_Demucs"
    ]
    
    base_dir = Path(".")
    
    # We want to use the current python executable to call "uv" module
    uv_python = sys.executable
    
    for folder_name in songs_to_process:
        folder_path = base_dir / folder_name
        audio_path = folder_path / "song.mp3"
        
        if not audio_path.exists():
            print(f"[Skip] {audio_path} not found.")
            continue
            
        print(f"\n=== Running Demucs for {folder_name} ===")
        
        output_dir = folder_path / "separated"
        
        cmd = [
            uv_python, "-m", "uv", "tool", "run",
            "--python", "3.10",
            "--with", "soundfile",
            "demucs",
            "-n", "htdemucs",
            "--mp3",
            "--two-stems", "vocals",
            "-o", str(output_dir),
            str(audio_path)
        ]

        try:
            print(f"Executing: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            print(f"[Success] Demucs finished for {folder_name}")
        except subprocess.CalledProcessError as e:
            print(f"[Error] Demucs failed for {folder_name}: {e}")
        except Exception as e:
            print(f"[Error] Unexpected error for {folder_name}: {e}")

if __name__ == "__main__":
    run_demucs_new()
