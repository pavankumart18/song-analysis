import os
import sys
import subprocess
from pathlib import Path

class DemucsRunner:
    def __init__(self, output_dir="separated"):
        self.output_dir = Path(output_dir)
        self.model = "htdemucs"

    def separate(self, audio_path, output_root=None):
        """
        Separates audio into vocals and no_vocals.
        output_root: Directory where 'separated' folder will be created. 
                     If None, uses the audio file's parent directory.
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if output_root is None:
            output_root = audio_path.parent

        song_name = audio_path.stem
        # Demucs structure: output_root/separated/htdemucs/song_name/vocals.wav
        # We enforce our own 'separated' subfolder to keep things clean like the user's structure
        output_dir = Path(output_root) / "separated"
        
        target_dir = output_dir / self.model / song_name
        vocals_path = target_dir / "vocals.wav"
        no_vocals_path = target_dir / "no_vocals.wav"

        # Check if already exists
        if vocals_path.exists() and no_vocals_path.exists():
            print(f"[Demucs] Found existing stems for {song_name}. Skipping separation.")
            return str(vocals_path), str(no_vocals_path)

        print(f"[Demucs] Separating {audio_path.name} with model {self.model}...")
        
        # Construct command
        # --two-stems=vocals forces generation of vocals.wav and no_vocals.wav (the rest mixed)
        cmd = [
            sys.executable, "-m", "demucs",
            "-n", self.model,
            "--two-stems", "vocals",
            "-o", str(output_dir),
            str(audio_path)
        ]

        try:
            subprocess.run(cmd, check=True)
            print("[Demucs] Separation complete.")
        except subprocess.CalledProcessError as e:
            print(f"[Demucs] Error during separation: {e}")
            raise

        if not vocals_path.exists():
            raise FileNotFoundError(f"Expected output file missing: {vocals_path}")

        return str(vocals_path), str(no_vocals_path)

if __name__ == "__main__":
    # Test stub
    import sys
    if len(sys.argv) > 1:
        runner = DemucsRunner()
        v, nv = runner.separate(sys.argv[1])
        print(f"Vocals: {v}")
        print(f"No Vocals: {nv}")
