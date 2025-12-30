# Song Analysis Pipeline

This project processes a dataset of songs to separate vocals from instruments, segment the vocals based on activity, and reconstruct the full mix for validation.

## Workflow

The pipeline consists of three main steps:

1.  **Organization (`organize_dataset.py`)**:
    *   Scans the root directory for `.mp3` files.
    *   Creates a clean, simplified folder for each song (e.g., `Song Name - Artist.mp3` -> `song_name/`).
    *   Moves the source file to `song_name/song.mp3`.

2.  **Separation (`process_folders.py`)**:
    *   Iterates through each song folder.
    *   Runs **Demucs** (using `uvx/uv`) to separate the song into `vocals.mp3` and `no_vocals.mp3`.
    *   Output path: `[song_folder]/separated/htdemucs/song/`.

3.  **Analysis & Reconstruction (`main.py`)**:
    *   Process each song folder.
    *   **Segmentation**: Detects vocal activity and slices both vocal and backing tracks into aligned segments (stored in `segments_vocals/` and `segments_nonvocals/`).
    *   **Reconstruction**: Stitches segments back together to create `reconstructed_mix.mp3`.
    *   **Validation**: Generates `direct_mix.mp3` (simple sum of stems) and compares it with the reconstructed mix using Signal-to-Noise Ratio (SNR) and Correlation metrics to ensure quality.

## Usage

### Prerequisites
- Python 3.10+
- `uv` package manager (automatically installed/used by scripts)
- FFmpeg (must be in PATH)

### Running the Pipeline

To run the full pipeline (separation -> analysis):

```bash
python process_folders.py
python main.py
```

*Note: `process_folders.py` will skip songs that have already been separated.*

## Output Structure

For each song (e.g., `song_name/`):

*   `song.mp3`: Original source.
*   `separated/`: Demucs output (vocals/no_vocals).
*   `segments_vocals/`: Individual active vocal clips.
*   `segments_nonvocals/`: Corresponding backing track clips.
*   `reconstructed_mix.mp3`: Recombined audio (validation artifact).
*   `direct_mix.mp3`: Raw sum of stems (reference artifact).
*   `reconstructed_vocals.mp3` & `reconstructed_nonvocals.mp3`: Intermediate full-length tracks.
