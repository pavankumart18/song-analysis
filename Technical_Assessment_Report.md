# Technical Assessment Report: Evaluation of Demucs vs SAM for Indian Source Separation & Segmentation

## 1. Executive Summary

The evaluation of Demucs and SAM against the Manual Ground Truth for Indian source separation and segmentation reveals distinct strengths and weaknesses in both AI models. Demucs demonstrates superior stability and alignment with manual segmentation, particularly in vocal separation, though it occasionally includes background noise. SAM excels in noise suppression but suffers from instrumental confusion, often mistaking instruments like flutes and violins for vocals. Overall, Demucs is closer to manual quality in terms of segment count and structure detection, while SAM requires improvements in instrument differentiation.

## 2. Methodology Overview

The comparison framework employed involves two primary techniques: Waveform and Spectrogram Masking. Demucs utilizes waveform-based separation, while SAM employs spectrogram masking. Manual segmentation serves as the baseline or Ground Truth, providing a reference for evaluating the accuracy and fidelity of the AI models in detecting song structures such as Pallavi and Interludes.

## 3. Quantitative Performance Metrics

| Song                             | Manual (GT) | Demucs | SAM  |
|----------------------------------|-------------|--------|------|
| Ghallu Ghallu                    | 13          | 8      | 6    |
| Mari Antaga SVSC Movie           | 9           | 7      | 4    |
| Naa Autograph Sweet Memories     | 13          | 7      | 8    |
| Narasimha - Narasimha            | 7           | 7      | 2    |
| Narasimha Yekku Tholi Mettu      | 11          | 7      | 2    |
| Nuvvostanante Nenoddantana       | 13          | 5      | 6    |
| Oh Sita Hey Rama                 | 8           | 11     | 8    |
| Pilichina Ranantava Song With    | 11          | 9      | 9    |
| Raja Edo Oka Ragam               | 9           | 7      | 3    |
| Robo                             | 13          | 4      | 6    |

**Discrepancies**: SAM consistently under-segments compared to Manual, particularly evident in songs like "Narasimha - Narasimha" and "Narasimha Yekku Tholi Mettu". Demucs generally aligns more closely with Manual segment counts but occasionally over-segments, as seen in "Oh Sita Hey Rama".

## 4. Qualitative Error Analysis (Thematic)

### Spectral Confusion
Both Demucs and SAM exhibit issues with spectral confusion, particularly in distinguishing between vocals and instruments such as violins and flutes. This confusion is more pronounced in SAM, which often misclassifies instrumental sounds as vocals, impacting the accuracy of vocal segment detection.

### VAD Sensitivity
Voice Activity Detection (VAD) sensitivity varies between the models. Demucs tends to include more background noise within vocal segments, whereas SAM is more effective at noise suppression. However, SAM's aggressive noise reduction sometimes leads to the misclassification of instrumental sounds as vocals.

### Structural Integrity
Demucs generally captures the Manual structure more faithfully, detecting Pallavi and Interludes with higher accuracy. SAM struggles with structural integrity, often failing to detect key song structures, as seen in "Mari Antaga SVSC Movie" and "Narasimha - Narasimha".

## 5. Song-Specific Technical Audit

### Ghallu Ghallu
- **Segments**: Manual - 13, Demucs - 8, SAM - 6
- **Issue**: Under-segmentation by SAM.
- **Root Cause**: Instrumental confusion and model size limitations.
- **Impact**: Critical.

### Robo
- **Segments**: Manual - 13, Demucs - 4, SAM - 6
- **Issue**: Significant under-segmentation by Demucs.
- **Root Cause**: Continuous signal misinterpretation.
- **Impact**: Critical.

### Nuvvostanante Nenoddantana
- **Segments**: Manual - 13, Demucs - 5, SAM - 6
- **Issue**: Under-segmentation by both models.
- **Root Cause**: Difficulty in differentiating humming from vocals.
- **Impact**: Critical.

### Narasimha - Narasimha
- **Segments**: Manual - 7, Demucs - 7, SAM - 2
- **Issue**: Severe under-segmentation by SAM.
- **Root Cause**: Inadequate model training for complex vocal-instrument differentiation.
- **Impact**: Critical.

## 6. Recommendations

For the production pipeline, Demucs is recommended as the primary model for source separation and segmentation due to its closer alignment with manual segmentation and structural integrity. Enhancements in noise suppression and labeling accuracy are advised. SAM requires significant improvements in instrument differentiation and structural detection before it can be considered a reliable alternative. Further training with diverse datasets may enhance SAM's performance in these areas.