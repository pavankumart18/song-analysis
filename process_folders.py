import os
import subprocess
import sys

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    # Iterate over subdirectories
    for item in os.listdir(root_dir):
        folder_path = os.path.join(root_dir, item)
        if os.path.isdir(folder_path):
            song_path = os.path.join(folder_path, "song.mp3")
            if os.path.exists(song_path):
                print(f"Processing folder: {item}")
                
                # Check for existing separated content to avoid re-run if successful?
                # But previous run failed, so likely empty separated folder.
                # Demucs usually skips if output exists.
                
                # Demucs usually skips if output exists.
                
                # Removed --with torchcodec because it was causing DLL loading issues on Windows.
                # Added --with soundfile because torchaudio needs a backend to save files on Windows.
                # System ffmpeg is available and should be used instead.
                # Added --mp3 and --mp3-bitrate 320 to save as MP3 instead of WAV.
                cmd = [sys.executable, "-m", "uv", "tool", "run", "--python", "3.10", "--with", "soundfile", "demucs", "--two-stems=vocals", "-n", "htdemucs", "--mp3", "--mp3-bitrate", "320", "song.mp3"]
                
                try:
                    # capture_output=False might define clearer logs if running manually, 
                    # but for background command, capturing stdout is safer or we redirect to file.
                    # We'll rely on command_status output.
                    result = subprocess.run(cmd, cwd=folder_path, shell=False, capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"Successfully processed {item}")
                    else:
                        print(f"Error processing {item}: {result.stderr}")
                except Exception as e:
                    print(f"Exception for {item}: {e}")

if __name__ == "__main__":
    main()
