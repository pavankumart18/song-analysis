# The Ghost in the Machine: AI & Indian Music

## 🎵 Project Overview

**Can Artificial Intelligence Really Understand Indian Music?**

For an AI accustomed to 4/4 drum beats and Western pop structures, Indian music is a labyrinth. It is a continuous tapestry of melody—the *Raga*—weaving seamlessly between vocalist and instrument. The line where a singer stops and a violin begins is often blurry, even to the human ear.

This project launches an ambitious experiment: **Could we build an automated pipeline to listen to a Telugu/Indian song and break it down into its cultural soul—Pallavi, Charanam, and Interludes?**

We built a bespoke signal processing engine that listens, separates, and mathematically proves structure, comparing **Manual Annotation (Ground Truth)** against two AI heavyweights: **Demucs (HTDemucs)** and **SAM-Audio (Segment Anything Model)**.

---

## 🛠️ The Pipeline: Building the Brain

We didn't just ask an LLM to guess. We built a robust processing pipeline:

1.  **Input**: Raw Audio (MP3/WAV).
2.  **Source Separation**:
    *   *Path A*: **Demucs** (Hybrid Transformer) - The "Audio Purist". Operates on raw waveforms.
    *   *Path B*: **SAM-Audio** - The "New Contender". Uses spectrogram masking and audio embeddings.
3.  **Vocal Activity Detection (VAD)**: Scanning the isolated vocal stems to detect "Blocks" of energy.
4.  **Fingerprinting**: Extracting Melodic Chroma Signatures to track relationships between blocks (e.g., verifying if a Pallavi repeats).
5.  **LLM Contextualization**: Using Large Language Models to interpret the timestamps and apply cultural labels (Pallavi, Charanam) based on duration and position.
6.  **Output**: A structured JSON file and an interactive, verified comparative dashboard.

---

## 📊 Technical Assessment Report

### Executive Summary

After evaluating 8+ complex Indian songs, **Demucs emerges as the superior model** for this specific task. It demonstrates superior stability in vocal separation and segment detection. **SAM-Audio**, while powerful for noise suppression, suffers from "instrumental confusion"—misclassifying instruments like violins and flutes as human vocals.

### Comparison Matrix

| Feature | 🩷 Demucs (HTDemucs) | 🔵 SAM-Audio |
| :--- | :--- | :--- |
| **Approach** | Waveform-based separation | Spectrogram/Embedding Masking |
| **Vocal Preservation** | **High (98%)** - Reliable, steady. | Mixed (85%) - Often over-masks. |
| **Noise Suppression** | Moderate | **Aggressive** - Very clean backgrounds. |
| **Structure Detection** | **Stable** - Consistent Pallavi/Charanam. | Erratic - Often misses interludes. |
| **Hallucination Rate** | Low | **High** - Confuses instruments for voices. |

### The "Violin" Problem (Failure Mode)

One of the most significant findings was the **Spectral Confusion** in SAM.
*   **Observation**: In songs like *Naa Autograph*, SAM continuously merged the Chorus and Verse.
*   **Cause**: Indian violin styles often mimic the sliding pitch of the human voice (*Gamakam*).
*   **Result**: SAM, trained partly on visual spectrograms, "saw" the frequency line of a violin and confidently labeled it **VOCAL**, destroying the structural integrity of the analysis.

### Song-by-Song Verdict

1.  **Ghallu Ghallu**: **Demucs Wins**. SAM over-segmented and confused flutes for vocals.
2.  **Mari Antaga**: **Demucs Wins**. Provided detailed segmentation of multiple interludes.
3.  **Narasimha**: **Demucs Wins**. SAM completely failed, missing almost all interludes and simplifying the song into just 2 blocks.
4.  **Robo**: **Demucs Wins**. More realistic segmentation, though challenges remain with continuous lyrics.

---

## 📂 Repository Structure

The data is organized to keep the repo lightweight, with audio stored as MP3s.

*   `index.html`: The main "Story" interface.
*   `dashboard.html`: The interactive comparative dashboard.
*   `data/`: Contains the analyzed song folders.
    *   `[Song]_Manual/`: Ground truth data.
    *   `[Song]_Demucs/`: Demucs-generated stems and structure.
    *   `[Song]_SAM/`: SAM-generated stems and structure.
*   `generate_full_comparison.py`: The script that powers the dashboard generation.

---

## 💻 How to Use

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/pavankumart18/song-analysis.git
    ```
2.  **Experience the Data**:
    *   Open `index.html` in your browser to read the visual story.
    *   Click "Enter Dashboard" to access the raw comparision tools.
    *   Use the **3-Column View** to play specific segments (e.g., click "Charanam 1" in the Demucs column to hear exactly what the AI isolated).

---

*This project is part of an ongoing research initiative into AI & Cultural Audio Analysis.*
