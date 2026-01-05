import os
import subprocess
from pathlib import Path
import sys

def merge_audio_files(file_list, output_path):
    """
    Merges a list of audio files using ffmpeg concat demuxer.
    """
    if not file_list:
        return

    # Create a temporary list file for ffmpeg
    list_file_path = output_path.parent / f"{output_path.stem}_concat_list.txt"
    try:
        with open(list_file_path, 'w', encoding='utf-8') as f:
            for file_path in file_list:
                # Use absolute path with forward slashes for ffmpeg compatibility
                safe_path = file_path.absolute().as_posix()
                f.write(f"file '{safe_path}'\n")
        
        # ffmpeg command to concat
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(list_file_path),
            "-c", "copy", 
            str(output_path)
        ]
        
        # print(f"Merging {len(file_list)} files to {output_path.name}...")
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[Success] Created: {output_path}")

    except subprocess.CalledProcessError as e:
        print(f"[Error] Failed to merge files for {output_path}: {e}")
    except Exception as e:
        print(f"[Error] An unexpected error occurred: {e}")
    finally:
        # Clean up list file
        if list_file_path.exists():
            os.remove(list_file_path)

def process_song_folder(song_folder):
    song_path = Path(song_folder)
    results_path = song_path / "results"
    
    if not results_path.exists():
        # print(f"Skipping {song_path.name}: 'results' folder not found.")
        return

    # Pattern matching for isolated (vocals) and residual (no_vocals) chunks
    # We look for files ending with _isolated.wav and _residual.wav
    # Assuming filenames act as sort keys (chunk_000, chunk_001...)
    
    isolated_files = sorted(list(results_path.glob("*_isolated.wav")))
    residual_files = sorted(list(results_path.glob("*_residual.wav")))
    
    # 1. Merge Isolated -> vocals.wav
    if isolated_files:
        print(f"--> Found {len(isolated_files)} isolated chunks in {song_path.name}")
        # Saving as vocals.wav in the song directory
        output_vocals = song_path / "vocals.wav"
        merge_audio_files(isolated_files, output_vocals)
    else:
        pass # print(f"No isolated chunks found in {song_path.name}")

    # 2. Merge Residual -> no_vocals.wav
    if residual_files:
        print(f"--> Found {len(residual_files)} residual chunks in {song_path.name}")
        # Saving as no_vocals.wav in the song directory
        output_novocals = song_path / "no_vocals.wav"
        merge_audio_files(residual_files, output_novocals)
    else:
        pass # print(f"No residual chunks found in {song_path.name}")

def main():
    # Assume 'songs' directory is in the current working directory
    # or allow passing via command line
    base_dir = Path("songs")
    
    if len(sys.argv) > 1:
        base_dir = Path(sys.argv[1])
    
    if not base_dir.exists():
        print(f"Error: Directory '{base_dir}' not found.")
        print("Usage: python merge_chunks.py [path_to_songs_folder]")
        return

    print(f"Scanning for songs in: {base_dir.absolute()}")
    
    for item in base_dir.iterdir():
        if item.is_dir():
            process_song_folder(item)

if __name__ == "__main__":
    main()
