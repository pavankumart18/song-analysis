import sys
import subprocess
from pathlib import Path

def run_demucs_on_demucs_folders():
    base_dir = Path(".")
    # Find all folders ending with _Demucs
    demucs_folders = [d for d in base_dir.iterdir() if d.is_dir() and d.name.endswith("_Demucs")]
    
    # We want to use the current python executable to call "uv" module
    uv_python = sys.executable
    
    for folder_path in demucs_folders:
        audio_path = folder_path / "song.mp3"
        
        if not audio_path.exists():
            print(f"[Skip] {audio_path} not found.")
            continue
            
        print(f"\n=== Running Demucs for {folder_path.name} ===")
        
        output_dir = folder_path / "separated"
        
        # Command using python -m uv tool run
        # We add --with soundfile to ensure robust audio handling on Windows
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
            # shell=False is safer when passing list of args
            print(f"Executing: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            print(f"[Success] Demucs finished for {folder_path.name}")
        except subprocess.CalledProcessError as e:
            print(f"[Error] Demucs failed for {folder_path.name}: {e}")
        except Exception as e:
            print(f"[Error] Unexpected error for {folder_path.name}: {e}")

if __name__ == "__main__":
    run_demucs_on_demucs_folders()
