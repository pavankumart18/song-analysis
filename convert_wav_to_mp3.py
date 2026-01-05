import os
import subprocess
from pathlib import Path

def convert_wav_to_mp3(root_dir):
    root_path = Path(root_dir)
    
    # Walk through all directories
    for valid_ext in ['*.wav']:
        for file_path in root_path.rglob(valid_ext):
            mp3_path = file_path.with_suffix('.mp3')
            
            # Check if MP3 already exists
            if mp3_path.exists():
                print(f"Skipping {file_path.name}, MP3 exists.")
                continue
                
            print(f"Converting {file_path} to MP3...")
            
            # Run ffmpeg
            # -i input -vn (no video) -ar 44100 -ac 2 -b:a 192k output
            cmd = [
                "ffmpeg", "-y", "-i", str(file_path),
                "-vn", "-ar", "44100", "-ac", "2", "-b:a", "192k",
                str(mp3_path)
            ]
            
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"Successfully converted to {mp3_path.name}")
            except subprocess.CalledProcessError as e:
                print(f"Error converting {file_path.name}: {e}")
            except FileNotFoundError:
                print("Error: ffmpeg not found. Please install ffmpeg.")
                return

if __name__ == "__main__":
    # Target the 'data' directory
    base_dir = Path(r"c:\Users\admin\Desktop\song analysis\data")
    if base_dir.exists():
        convert_wav_to_mp3(base_dir)
    else:
        print("Data directory not found.")
