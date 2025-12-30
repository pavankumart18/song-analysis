import os
import shutil
import re
import subprocess
import sys

def clean_name(filename):
    # Remove extension
    name = os.path.splitext(filename)[0]
    # Remove artist part (assuming " - Artist" format)
    if " - " in name:
        name = name.split(" - ")[0]
    # Simplify: lowercase, replace spaces with underscores, alphanumeric only
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    clean_name = clean_name.lower().strip().replace(' ', '_')
    return clean_name

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    files = [f for f in os.listdir(root_dir) if f.endswith('.mp3')]
    
    # Exclude files that look like outputs or specific files we shouldn't touch if any
    # We'll assume all mp3s in root are songs to be processed
    exclude_keywords = ['reconstructed', 'direct_mix', 'segment', 'vocals', 'no_vocals']
    files = [f for f in files if not any(k in f for k in exclude_keywords)]

    print(f"Found {len(files)} songs to process.")

    for file in files:
        if file == "song.mp3":
            # Already renamed? Skip or handle?
            continue
            
        folder_name = clean_name(file)
        folder_path = os.path.join(root_dir, folder_name)
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created folder: {folder_path}")
        
        src = os.path.join(root_dir, file)
        dst = os.path.join(folder_path, "song.mp3")
        
        if not os.path.exists(dst):
            print(f"Moving {file} -> {dst}")
            shutil.move(src, dst)
        else:
            print(f"File already exists at {dst}, skipping move.")

        # Run demucs command
        # It's better to run this sequentially to avoid OOM or CPU saturation if running parallel
        print(f"Running demucs in {folder_name}...")
        
        # The command provided by user
        # Used python -m uv tool run because uv/uvx might not be in PATH
        cmd = [sys.executable, "-m", "uv", "tool", "run", "--python", "3.10", "--with", "torchcodec", "demucs", "--two-stems=vocals", "-n", "htdemucs", "song.mp3"]
        
        try:
            # shell=False is better with list arguments
            result = subprocess.run(cmd, cwd=folder_path, shell=False, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Successfully processed {folder_name}")
            else:
                print(f"Error processing {folder_name}: {result.stderr}")
        except Exception as e:
            print(f"Exception running command for {folder_name}: {e}")

if __name__ == "__main__":
    main()
