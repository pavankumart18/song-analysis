# Song Analysis Pipeline

This project processes a dataset of songs to separate vocals from instruments, segment the vocals based on activity, and reconstruct the full mix for validation.

## Workflow

The pipeline consists of three main steps:

1.  **Organization (`organize_dataset.py`)**:
    *   Scans the root directory for `.mp3` files.
    *   Creates a clean, simplify folder for each song (e.g., `Song Name - Artist.mp3` -> `song_name/`).
    *   Moves the source file to `song_name/song.mp3`.

2.  **Separation (`process_folders.py`)**:
    *   Iterates through each song folder.
    *   Runs **Demucs** (using `uvx/uv`) to separate the song into `vocals.mp3` and `no_vocals.mp3`.
    *   Output path: `[song_folder]/separated/htdemucs/song/`.

## Analysis & Reconstruction (`main.py`)
    *   **Process**: Analyzes each song folder.
    *   **Structure Analysis**: Uses energy-based block detection + LLM to identify 'Pallavi', 'Charanam', and 'Interludes'.
    *   **Verification**: Generates a **Markdown Report** comparing detected segments with LLM-estimated Song Metadata (Intro length, Vocal Start).
    *   **Player Generation**: Creates a `song_player.html` for interactive playback of segmented parts.
    *   **Validation**: Slices the original audio into labeled parts (`segmented_parts/`) for manual verification.

## Verification & Reports

The system now generates a **Verification Report** (`[SongName]_verification_report.md`) for each song. 

This report provides:
1.  **Expected Metadata**: Estimates from the LLM about where the vocals *should* start and typical structure hints.
2.  **Detected Segmentation**: The actual start/end timestamps and labels found by the analysis engine.
3.  **Comparision**: A side-by-side view to quickly spot if "Pallavi" started at 0:33 (correct) vs 0:10 (noise).

## Output Structure

For each song (e.g., `song_name/`):

*   `song.mp3`: Original source.
*   `separated/`: Demucs output (vocals/no_vocals).
*   `song_structure.json`: High-level structural data (Pallavi, Charanam, etc.).
*   `*_verification_report.md`: Report comparing detected vs expected structure.
*   `song_player.html`: Interactive HTML5 player.
*   `segmented_parts/`: Folder containing actual MP3 slices of each detected section (Intro, Pallavi, etc.) for listening.
*   `song_reconstructed_master.mp3`: Full concatenation of the sliced parts (should sound like the original).
