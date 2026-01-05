# Indian Music Analysis Dashboard

A premium analytical dashboard for evaluating and comparing Source Separation and Segmentation models on Indian film music. This project provides a side-by-side comparison between **Manual Annotation (Ground Truth)**, **Demucs (HTDemucs)**, and **SAM (Segment Anything Model)**.

## 🎵 Project Overview

The goal of this project is to analyze the structure of complex Indian songs (Telugu/Tamil) by identifying segments like *Pallavi*, *Charanam*, *Interludes*, and *Humming*. We evaluate how well automated AI models perform against human labeling.

## ✨ Features

-   **Comparative Dashboard**: A centralized `index.html` interface to browse all analyzed songs.
-   **3-Column View**: Dedicated comparison pages for each song, displaying Manual, Demucs, and SAM segments side-by-side.
-   **Interactive Audio Players**: Click on any segment (e.g., "Charanam 1") to instantly play that meaningful chunk of audio.
-   **Visual Metrics**: Color-coded cues to identify which methods are available for each song.

## 🛠️ Methodology

We track three versions of analysis for each song:

1.  **🟢 Manual (Ground Truth)**:
    *   Human-verified timestamps and labels.
    *   Serves as the benchmark for accuracy.
    *   Includes verified lyrics and section separations.

2.  **🩷 Demucs (HTDemucs)**:
    *   Uses the Hybrid Transformer Demucs model for source separation.
    *   Algorithmic block detection runs on the isolated vocal stem.
    *   **Performance**: Generally high accuracy (85-90%), good at identifying main structural transitions.

3.  **🔵 SAM (Segment Anything Model)**:
    *   Uses Meta's SAM to segment the visual spectrogram of the audio.
    *   **Performance**: Experimental. Tends to over-segment or hallucinate vocals during noisy instrumental sections.

## 🚀 Comparison Results

An automated LLM-based report (`SAM_vs_Demucs_Comparison_Report.md`) was generated to analyze the findings.
*   **Winner**: **Demucs**
*   **Key Findings**: Demucs provided more realistic granular breakdowns closer to human perception. SAM struggled with the dense spectral overlap common in Indian film music, leading to "hallucinations" of vocal blocks.

## 📂 Project Structure

*   `index.html`: Main entry point.
*   `compare_[Song_Name].html`: Individual comparison views.
*   `[song_name]_Manual/`: Contains manual labels and sliced audio.
*   `[song_name]_Demucs/`: Contains Demucs-separated stems and algorithmic analysis.
*   `[song_name]_SAM/`: Contains SAM-based segmentation data.

## 💻 How to Use

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/pavankumart18/song-analysis.git
    ```
2.  **Open the Dashboard**:
    Simply open `index.html` in any modern web browser.
3.  **Browse & Listen**:
    Click on a song to see the comparison. Click on segments in the columns to listen to specific parts.

---
*Created by [Your Name/Team] for Advanced Audio Analysis.*
