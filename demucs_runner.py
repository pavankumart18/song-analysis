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
        
        # Check for pre-existing SAM separation
        sam_target_dir = output_dir / "sam" / song_name
        sam_vocals = sam_target_dir / "vocals.wav"
        sam_novocals = sam_target_dir / "no_vocals.wav"
        
        if sam_vocals.exists() and sam_novocals.exists():
            print(f"[Demucs] Found existing SAM stems for {song_name}. Using them.")
            return str(sam_vocals), str(sam_novocals)

        target_dir = output_dir / self.model / song_name
        vocals_path = target_dir / "vocals.wav"
        no_vocals_path = target_dir / "no_vocals.wav"

        # Check for .wav stems
        vocals_path_wav = target_dir / "vocals.wav"
        novocals_path_wav = target_dir / "no_vocals.wav"
        
        # Check for .mp3 stems
        vocals_path_mp3 = target_dir / "vocals.mp3"
        novocals_path_mp3 = target_dir / "no_vocals.mp3"

        if vocals_path_wav.exists() and novocals_path_wav.exists():
            print(f"[Demucs] Found existing WAV stems for {song_name}. Skipping separation.")
            return str(vocals_path_wav), str(novocals_path_wav)

        if vocals_path_mp3.exists() and novocals_path_mp3.exists():
            print(f"[Demucs] Found existing MP3 stems for {song_name}. Skipping separation.")
            return str(vocals_path_mp3), str(novocals_path_mp3)

        print(f"[Demucs] Separating {audio_path.name} with model {self.model}...")
        
        # Output is managed by command line demucs now, usually we don't call this method if we have batch pre-processed
        # But if we did, we would need to check which format we want to generate.
        # For now, this tool is mostly for checking existence during analysis pipeline.
        
        if not vocals_path_wav.exists() and not vocals_path_mp3.exists():
             raise FileNotFoundError(f"Expected output file missing: {vocals_path_wav} or {vocals_path_mp3}")

        return str(vocals_path_wav) if vocals_path_wav.exists() else str(vocals_path_mp3), \
               str(novocals_path_wav) if novocals_path_wav.exists() else str(novocals_path_mp3)

if __name__ == "__main__":
    # Test stub
    import sys
    if len(sys.argv) > 1:
        runner = DemucsRunner()
        v, nv = runner.separate(sys.argv[1])
        print(f"Vocals: {v}")
        print(f"No Vocals: {nv}")
