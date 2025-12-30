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

3.  **Analysis & Reconstruction (`main.py`)**:
    *   Process each song folder.
    *   **Segmentation**: Detects vocal activity and slices both vocal and backing tracks into aligned segments (stored in `segments_vocals/` and `segments_nonvocals/`).
    *   **Reconstruction**: Stitches segments back together to create `reconstructed_mix.mp3`.
    *   **Validation**: Generates `direct_mix.mp3` (simple sum of stems) and compares it with the reconstructed mix.

## Metrics & Validation Results

To validate the reconstruction quality, we compare the **Reconstructed Mix** (processed) against the **Direct Mix** (simple sum of stems). High correlations and SNR values indicate that the segmentation process successfully preserved the audio content without artifacts.

| Song Name | Segments Found | MAE (Mean Absolute Error) | SNR (Signal-to-Noise Ratio) | Correlation |
| :--- | :---: | :---: | :---: | :---: |
| **aakasham_digivachi** | 30 | 0.000257 | 40.83 dB | 1.0000 |
| **cheppave_chirugali** | 17 | 0.000303 | 35.69 dB | 0.9999 |
| **devuda_devuda** | 31 | 0.000431 | 28.67 dB | 0.9993 |
| **dheeradheera** | 17 | 0.000123 | 47.39 dB | 1.0000 |
| **edo_oka_raagam** | 36 | 0.000275 | 40.96 dB | 1.0000 |
| **gummadi_gummadi** | 26 | 0.000194 | 36.60 dB | 0.9999 |
| **manava_manava** | 19 | 0.000191 | 43.34 dB | 1.0000 |
| **my_name_is_billa** | 9 | 0.000088 | 54.69 dB | 1.0000 |
| **neeve** | 18 | 0.000151 | 47.47 dB | 1.0000 |
| **netho_cheppana** | 14 | 0.000204 | 42.78 dB | 1.0000 |
| **priyatama** | 22 | 0.000163 | 41.02 dB | 1.0000 |

### Metric Definitions
*   **MAE (Mean Absolute Error)**: Average absolute difference between the reconstructed signal and the original signal. Lower is better.
*   **SNR (Signal-to-Noise Ratio)**: Measures the ratio of signal power to noise (error) power. Higher values (>30-40dB) indicate excellent reconstruction quality.
*   **Correlation**: Pearson correlation coefficient. A value of **1.0000** means the waves are identical in shape.

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
