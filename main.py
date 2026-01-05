import argparse
import json
import csv
import sys
from pathlib import Path
from demucs_runner import DemucsRunner
from block_detector import BlockDetector
from llm_formatter import LLMFormatter
from player_generator import PlayerGenerator
# from lyrics_transcriber import LyricsTranscriber
from audio_slicer import AudioSlicer

def generate_verification_report(song_name, structure, metadata, expected_structure, output_dir):
    """
    Generates a readable report comparing detected structure with expected hints.
    """
    report_path = output_dir / f"{song_name}_verification_report.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Verification Report: {song_name}\n\n")
        
        f.write("## 1. LLM Estimated Structure (Training Data / Knowledge)\n")
        f.write("| Label | Start (s) | End (s) |\n")
        f.write("| :--- | :--- | :--- |\n")
        if expected_structure:
            for section in expected_structure:
                f.write(f"| {section['label']} | {section['start']} | {section['end']} |\n")
        else:
            f.write("| No Data | - | - |\n")
        
        f.write("\n## 2. Detected Segmentation (Audio Analysis)\n")
        f.write("| Index | Label | Start (s) | End (s) | Duration (s) |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        
        for i, section in enumerate(structure):
            dur = round(section['end'] - section['start'], 2)
            f.write(f"| {i} | **{section['label']}** | {section['start']} | {section['end']} | {dur} |\n")
            
        f.write("\n## 3. Verification & Comparison\n")
        f.write("- Compare the **LLM Estimated** 'Pallavi' start vs **Detected** 'Pallavi' start.\n")
        f.write("- Note: LLM estimates are often approximate (+/- 5-10s) whereas Detected timestamps are from the actual audio file.\n")
    
    print(f"[Report] Generated verification report: {report_path}")

def save_output(structure, output_base_path):
    """
    Saves the structure to JSON and CSV.
    """
    # Save JSON
    json_path = output_base_path.with_suffix('.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2)
    print(f"[Output] Saved JSON to {json_path}")

    # Save CSV
    csv_path = output_base_path.with_suffix('.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Label", "Start (s)", "End (s)"])
        for section in structure:
            writer.writerow([section.get("label", "Unknown"), section.get("start"), section.get("end")])
    print(f"[Output] Saved CSV to {csv_path}")

def process_song(audio_path):
    audio_path = Path(audio_path)
    if not audio_path.exists():
        print(f"Error: File {audio_path} does not exist.")
        return

    # Determine meaningful song name
    song_display_name = audio_path.stem
    if song_display_name.lower() in ['song', 'audio', 'vocals', 'input']:
        song_display_name = audio_path.parent.name
    
    song_display_name = song_display_name.replace("_", " ").title()

    output_name = f"{audio_path.stem}_structure"
    output_path = audio_path.parent / output_name
    
    # if output_path.with_suffix('.json').exists():
    #     print(f"Skipping {audio_path.name}, structure already exists.")
    #     return

    print(f"=== Processing {audio_path.name} ===")

    # 1. Source Separation
    demucs = DemucsRunner()
    try:
        vocals_path, no_vocals_path = demucs.separate(audio_path, output_root=audio_path.parent)
    except Exception as e:
        print(f"Separation failed: {e}")
        return

    # 2. Vocal Activity Scanning & Block Detection
    # Reduced window to 0.5s for better resolution. Increased threshold to 0.035 to ignore deeper noise/breathing.
    # Detect if we are processing a SAM folder
    is_sam_folder = "SAM" in audio_path.parent.name or "sam" in audio_path.parent.name
    
    detector = BlockDetector(window_duration=0.5, energy_threshold=0.035) 
    try:
        blocks = detector.process(vocals_path, is_sam=is_sam_folder)
    except Exception as e:
        print(f"Block detection failed: {e}")
        return

    if not blocks:
        print("No blocks detected.")
        return

    # 3. LLM Semantic Formatting & Validation
    formatter = LLMFormatter()
    
    # Get Metadata Hint (Optional, for context only)
    metadata = formatter.get_song_metadata(song_display_name)
    est_start = metadata.get("estimated_vocal_start", 0)
    print(f"[Main] LLM estimates vocals start at {est_start}s. Using as hint for labeling.")
    
    # Get Full Expected Structure for Comparison
    expected_structure = formatter.get_expected_structure(song_display_name)
    
    try:
        structure = formatter.generate_structure(blocks, song_name=song_display_name, estimated_start=est_start)
    except Exception as e:
        print(f"LLM formatting failed: {e}")
        return

    if not structure:
        print("LLM returned empty structure.")
        return

    # 4. Final Output
    # Save in the same directory as the input audio, or a specific output folder?
    # User said "formatted_structure.json".
    # I'll save it alongside the Separated files or the original file?
    # Let's frame it as song_name_structure.json in the current directory or song directory.
    # Given the previous context of song folders, let's try to save it in the song's folder if it exists, 
    # otherwise just current dir.
    
    output_name = f"{audio_path.stem}_structure"
    output_path = audio_path.parent / output_name
    
    save_output(structure, output_path)
    generate_verification_report(song_display_name, structure, metadata, expected_structure, audio_path.parent)
    
    # 5. Get Lyrics from LLM (Optional - Disabled for UI)
    lyrics_data = []
    
    # We use the structure we just generated to ask for lyrics per section
    # try:
    #     lyrics_map = formatter.generate_lyrics(song_display_name, structure)
    #     
    #     # Map back to time segments
    #     for section in structure:
    #         label = section.get('label')
    #         text = lyrics_map.get(label, "")
    #         
    #         # If text is empty, maybe it's an interlude
    #         if not text and "Interlude" in label:
    #             text = "[Instrumental]"
    #         
    #         if text:
    #             lyrics_data.append({
    #                 "text": text,
    #                 "start": section['start'],
    #                 "end": section['end']
    #             })
    #             
    # except Exception as e:
    #     print(f"Lyrics generation failed: {e}")

    # 6. Generate Player
    player_gen = PlayerGenerator()
    player_gen.generate(audio_path, output_path.with_suffix('.json'), lyrics_data=lyrics_data)
    
    # 7. Validation: Slice and Merge Master
    slicer = AudioSlicer()
    slicer.slice_and_merge(audio_path, structure)
    
    print(f"=== Completed {audio_path.name} ===\n")

def main():
    parser = argparse.ArgumentParser(description="Indian Song Segmentation Pipeline")
    parser.add_argument("input_path", help="Path to song (mp3/wav) or directory containing songs")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    input_path = Path(args.input_path)

    if input_path.is_file():
        process_song(input_path)
    elif input_path.is_dir():
        # Process usage: python main.py "path/to/folder_of_songs"
        # Or if the folder itself contains the audio:
        # Filter to only 'song.mp3' to avoid processing generated mixes
        files = list(input_path.rglob('song.mp3'))
        
        # Filter out separated files to avoid re-processing chunks (redundant if we check name, but good safety)
        files = [f for f in files if "separated" not in f.parts]
        
        print(f"Found {len(files)} audio files in {input_path}")
        for f in files:
            process_song(f)
    else:
        print("Invalid path.")

if __name__ == "__main__":
    main()
