# End-to-End Evaluation: AI Segmentation on Indian Music

## 📊 Technical Abstract

This research evaluates the efficacy of state-of-the-art AI separation models—**Demucs (Hybrid Transformer)** and **SAM (Segment Anything Model)**—in the structural segmentation of Indian music. Unlike Western pop, Indian music features continuous melodic tapestries (*Ragas*) where the vocal-instrumental boundary is often blurred.

We implemented a rigorous, quantitative pipeline comparing model predictions against **Manual Ground Truth** annotations for 10 complex songs. The evaluation focuses on **Vocal Isolation Accuracy (F1 Score)**, **Structural Alignment (IoU)**, and **Hallucination Rate (False Positive Rate)**.

**Key Findings:**
*   **Demucs** achieves a **~2x higher F1 Score** (Vocal Accuracy) than SAM.
*   **SAM** suffers from a **49.2% Vocal False Positive Rate (FPR)**, consistently misclassifying melodic instruments (Violin, Flute) as vocals.
*   **Demucs** provides significantly better structural alignment with an average **Mean IoU of 0.42** vs SAM's **0.26**.

---

## 🕵️ AI Forensic Analyst & Interactive Dashboard

We have developed a comprehensive **End-to-End Analysis Dashboard** to visualize these metrics. This is not just a chart; it is a forensic tool.

**Primary Interface:** [`end_to_end_dashboard.html`](./end_to_end_dashboard.html)

### Key Features:

1.  **🤖 AI Forensic Analyst**:
    *   Click on any segment in the timeline.
    *   The "Analyst" console provides an **LLM-generated explanation** for *why* a specific error occurred (e.g., *"CRITICAL ERROR: Hallucination - Model confused Violin for Vocals"*).
    *   It distinguishes between **Alignment Jitter** (minor timing errors) and **Ghost Segments** (hallucinations).

2.  **🚨 Visual Proof of Hallucinations**:
    *   The dashboard lists specific "Hallucination Events" in a table.
    *   **Clickable Metrics**: Clicking a red error value (e.g., **"15.2% Error"**) instantly redirects you to that exact moment in the song, analyzing the failure in real-time.

3.  **Real-Time "Karaoke" Visualization**:
    *   As the audio plays, the dashboard **highlights the active segments** across all three rows (Manual, Demucs, SAM) simultaneously.
    *   This allows for instant visual validation of where the models diverge from the Ground Truth.

---

## 📈 Quantitative Evaluation

### Aggregate Metrics (Average across 10 Songs)

| Metric | Demucs | SAM | Interpretation |
| :--- | :--- | :--- | :--- |
| **Vocal F1 Score** | **High** | Low | Demucs is significantly more accurate at identifying true vocal regions. |
| **Mean IoU** | **0.418** | 0.264 | Demucs segments align 40% better with human-perceived structure. |
| **Vocal FPR (Error Rate)** | **20.8%** | **49.2%** | **CRITICAL FAILURE**: SAM spends half the instrumental time thinking it hears vocals. |
| **Boundary Error** | **~29s** | ~58s | SAM's boundaries are often loose or completely misplaced. |

---

## 🎻 The "Violin Problem": Hallucination Analysis

A major focus of this study was **Instrumental Confusion**. Indian instruments often mimic the sliding pitch of the human voice (*Gamakam*).

*   **The Issue**: SAM, trained heavily on spectrogram visual features, "sees" a violin line and labels it as a Vocal.
*   **Quantifiable Proof**:
    *   In *Narasimha*, SAM hallucinated **90%** of the instrumental sections as vocals.
    *   In *Ghallu Ghallu*, SAM confused the flute interludes for singing.
*   **Demucs Advantage**: Operating on the raw waveform, Demucs successfully distinguishes the *timbre* of a voice from an instrument, resulting in a much lower FPR (20%).

---

## 💻 How to Run the Analysis

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/pavankumart18/song-analysis.git
    cd song-analysis
    ```

2.  **View the Dashboard**:
    *   Open **`index.html`** in your browser.
    *   Click the top button **"End-to-End Analysis Dashboard"**.
    *   *Alternatively, open `end_to_end_dashboard.html` directly.*

3.  **Re-Run Metrics (Optional)**:
    If you want to re-process the data or add new songs:
    ```bash
    # 1. Generate core metrics
    python scripts/advanced_evaluation.py

    # 2. Generate forensic proof logs
    python scripts/generate_confusion_proof.py

    # 3. Build the dashboard
    python generate_final_dashboard.py
    ```

---

## 📝 Conclusion

For the task of structural segmentation of Indian music:
*   **Demucs is the production-ready choice.** It respects the silence of interludes and consistently identifies vocal blocks.
*   **SAM is not currently viable** for this specific task without fine-tuning, as its aggressive "segment everything" approach leads to massive instrumental confusion.

*Data generated on 2026-01-06.*
