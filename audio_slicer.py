import subprocess
import os
from pathlib import Path

class AudioSlicer:
    def __init__(self):
        pass

    def slice_and_merge(self, audio_path, structure):
        """
        Slices the audio file into segments and merges them back 
        to verify that the segmentation is seamless.
        """
        audio_path = Path(audio_path)
        output_dir = audio_path.parent / "segmented_parts"
        output_dir.mkdir(exist_ok=True)
        
        song_name = audio_path.stem
        segments_list_file = output_dir / "segments.txt"
        
        with open(segments_list_file, 'w', encoding='utf-8') as f:
            for i, section in enumerate(structure):
                start = section['start']
                duration = section['end'] - start
                label = section['label'].replace(" ", "_")
                segment_name = f"{i:02d}_{label}.mp3"
                segment_path = output_dir / segment_name
                
                # Slice command: ffmpeg -ss start -t duration -i input -c copy output
                cmd = [
                    "ffmpeg", "-y",
                    "-ss", str(start),
                    "-t", str(duration),
                    "-i", str(audio_path),
                    "-c:a", "libmp3lame", "-q:a", "2", # Re-encoding slightly for better compatibility, or use 'copy'
                    str(segment_path)
                ]
                subprocess.run(cmd, capture_output=True)
                
                # Add to list for concatenation
                # Note: Windows paths in ffmpeg concat need some escaping
                abs_path = str(segment_path.absolute()).replace("\\", "/")
                f.write(f"file '{abs_path}'\n")

        # Merge them back: ffmpeg -f concat -safe 0 -i list -c copy merged.mp3
        merged_path = audio_path.parent / f"{song_name}_reconstructed_master.mp3"
        merge_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(segments_list_file),
            "-c", "copy",
            str(merged_path)
        ]
        
        print(f"[AudioSlicer] Slicing {len(structure)} parts and merging to master...")
        subprocess.run(merge_cmd, capture_output=True)
        print(f"[AudioSlicer] Created Master: {merged_path}")
        return merged_path

if __name__ == "__main__":
    pass
