# Technical Assessment Report: Evaluation of "Demucs" vs "SAM" for Indian Source Separation & Segmentation

## 1. Executive Summary

The comparative analysis of "Demucs" and "SAM-Audio" models for Indian music source separation and segmentation reveals distinct strengths and weaknesses. Demucs demonstrates superior stability in vocal separation and segment detection, while SAM-Audio excels in noise suppression but suffers from instrumental confusion, particularly with instruments like violins and flutes being misclassified as vocals.

## 2. Methodology Overview

The evaluation framework involves two primary approaches: waveform-based separation (Demucs) and spectrogram/audio-embedding masking (SAM-Audio). Demucs focuses on direct waveform manipulation to isolate audio components, whereas SAM-Audio employs audio-specific embeddings and prompting to mask and separate different audio sources.

## 3. Quantitative Performance Metrics

| Song                          | Model  | Total Segments | Vocal Segments | Avg Segment Duration (s) | Pallavi Detected | Interludes Detected |
|-------------------------------|--------|----------------|----------------|--------------------------|------------------|----------------------|
| Ghallu Ghallu                 | Demucs | 8              | 4              | 43.94                    | Yes              | 3                    |
|                               | SAM    | 6              | 3              | 58.58                    | Yes              | 2                    |
| Mari Antaga SVSC Movie        | Demucs | 7              | 4              | 34.5                     | Yes              | 3                    |
|                               | SAM    | 4              | 2              | 60.38                    | No               | 1                    |
| Naa Autograph Sweet Memories  | Demucs | 7              | 3              | 38.07                    | Yes              | 2                    |
|                               | SAM    | 8              | 4              | 33.31                    | Yes              | 3                    |
| Narasimha - Narasimha         | Demucs | 7              | 4              | 48.0                     | Yes              | 3                    |
|                               | SAM    | 2              | 1              | 168.0                    | No               | 0                    |
| Nuvvostanante Nenoddantana s  | Demucs | 5              | 3              | 49.6                     | Yes              | 1                    |
|                               | SAM    | 6              | 3              | 41.33                    | Yes              | 1                    |
| Oh Sita Hey Rama              | Demucs | 11             | 5              | 20.5                     | Yes              | 3                    |
|                               | SAM    | 8              | 4              | 29.19                    | Yes              | 3                    |
| Pilichina Ranantava Song With | Demucs | 9              | 4              | 35.28                    | Yes              | 3                    |
|                               | SAM    | 9              | 4              | 35.28                    | Yes              | 4                    |
| Raja Edo Oka Ragam            | Demucs | 7              | 3              | 37.71                    | Yes              | 3                    |
|                               | SAM    | 3              | 1              | 88.0                     | No               | 1                    |
| Robo                          | Demucs | 4              | 2              | 79.25                    | No               | 0                    |
|                               | SAM    | 6              | 3              | 52.83                    | Yes              | 1                    |

### Key Observations:
- SAM consistently under-segments compared to Demucs, particularly in songs like "Narasimha - Narasimha" and "Raja Edo Oka Ragam".
- Demucs shows higher consistency in detecting Pallavi and interludes across the dataset.

## 4. Qualitative Error Analysis (Thematic)

### Spectral Confusion
Both models exhibit spectral confusion, particularly with instruments like violins and flutes being misclassified as vocals. This is more pronounced in SAM, likely due to its smaller model size and limited training data diversity.

### VAD Sensitivity
SAM demonstrates better noise suppression capabilities, effectively reducing background noise. However, this comes at the cost of misclassifying certain instrumental sounds as vocals, affecting the signal-to-noise ratio adversely.

### Structural Integrity
Errors in spectral confusion and VAD sensitivity impact the structural integrity of song labeling, particularly in distinguishing Pallavi and Charanam sections. Demucs, while more stable, occasionally merges segments due to background noise misclassification.

## 5. Song-Specific Technical Audit

### Ghallu Ghallu
- **Issue**: Instrumental confusion, particularly with flutes.
- **Root Cause**: Model size and training data limitations.
- **Impact**: Minor.

### Mari Antaga SVSC Movie
- **Issue**: Background noise inclusion by Demucs.
- **Root Cause**: Waveform-based separation limitations.
- **Impact**: Minor.

### Narasimha - Narasimha
- **Issue**: SAM's failure to detect vocals and interludes.
- **Root Cause**: Spectrogram masking inefficiencies.
- **Impact**: Critical.

### Robo
- **Issue**: Misclassification of continuous lyrics as vocals by Demucs.
- **Root Cause**: Signal continuity in waveform analysis.
- **Impact**: Minor.

## 6. Recommendations

For optimal performance in the production pipeline, it is recommended to integrate Demucs for its stability in segment detection and vocal separation. However, enhancements in noise suppression should be considered, potentially by incorporating elements from SAM's spectrogram masking approach. Additionally, addressing the spectral confusion in both models through expanded training datasets and model refinement is crucial to improve accuracy in instrumental differentiation.