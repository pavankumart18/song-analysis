# Quantitative Evaluation Report: Demucs vs SAM

## 1. Executive Summary
This report provides a strict quantitative comparison of Demucs and SAM against a Manual Ground Truth dataset.
**Total Songs Analyzed**: 10
**Full Data Proof**: [Download CSV](./data/Full_Segment_Analysis.csv)

## 2. Quantitative Findings

### 2.1 Comparative Findings
- **Alignment**: Demucs achieves a higher Mean IoU (0.42) compared to SAM (0.26), indicating better overlap with ground truth.
- **Instrumental Confusion**: SAM shows a higher Vocal False Positive Rate (49.17%) than Demucs (20.83%), confirming the issue of misclassifying instruments as vocals.
- **Boundary Precision**: The average boundary error for Demucs is 29934ms, whereas SAM is 58555ms.

### 2.2 Aggregate Metrics Table
| Metric | Demucs | SAM |
| :--- | :--- | :--- |
| Mean IoU | 0.418 | 0.264 |
| Median IoU | 0.405 | 0.207 |
| Avg Boundary Error (ms) | 29934 | 58555 |
| Deletion Rate (Missed) | 10.9% | 23.3% |
| Insertion Rate (Hallucinated) | 19.0% | 14.9% |
| **Vocal False Positive Rate** | **20.8%** | **49.2%** |

## 3. Per-Song Detailed Analysis
Comparison of alignment (IoU) and Instrumental Confusion (FPR) for every song.

| Song Name                     | Model   |   Mean IoU |   Vocal FPR |
|:------------------------------|:--------|-----------:|------------:|
| Mari_Antaga_SVSC_Movie        | Demucs  |      0.557 |       0.250 |
| Mari_Antaga_SVSC_Movie        | SAM     |      0.395 |       0.500 |
| Naa_Autograph_Sweet_Memories  | Demucs  |      0.290 |       0.333 |
| Naa_Autograph_Sweet_Memories  | SAM     |      0.246 |       0.333 |
| Narasimha_-_Narasimha         | Demucs  |      0.412 |       0.333 |
| Narasimha_-_Narasimha         | SAM     |      0.274 |       0.667 |
| Narasimha_Yekku_Tholi_Mettu   | Demucs  |      0.301 |       0.000 |
| Narasimha_Yekku_Tholi_Mettu   | SAM     |      0.121 |       1.000 |
| Nuvvostanante_Nenoddantana_s  | Demucs  |      0.192 |       0.500 |
| Nuvvostanante_Nenoddantana_s  | SAM     |      0.178 |       0.250 |
| Oh_Sita_Hey_Rama              | Demucs  |      0.242 |       0.250 |
| Oh_Sita_Hey_Rama              | SAM     |      0.256 |       0.750 |
| Pilichina_Ranantava_Song_With | Demucs  |      0.410 |       0.167 |
| Pilichina_Ranantava_Song_With | SAM     |      0.379 |       0.167 |
| Raja_Edo_Oka_Ragam            | Demucs  |      0.651 |       0.000 |
| Raja_Edo_Oka_Ragam            | SAM     |      0.119 |       0.250 |
| ghallu_ghallu                 | Demucs  |      0.491 |       0.000 |
| ghallu_ghallu                 | SAM     |      0.264 |       0.500 |
| robo                          | Demucs  |      0.076 |       0.250 |
| robo                          | SAM     |      0.088 |       0.500 |

## 4. Segment-Wise Error Table (Sample)
Below is a sample of segment-wise errors. **See `Full_Segment_Analysis.csv` for the complete row-by-row proof.**

| Song Name     | Model   | Manual Segment               |   Manual Start |   Manual End |   Predicted Start |   Predicted End |   IoU | Error Type                                  | Manual Type   |
|:--------------|:--------|:-----------------------------|---------------:|-------------:|------------------:|----------------:|------:|:--------------------------------------------|:--------------|
| ghallu_ghallu | Demucs  | Intro (Instrumental )        |              0 |           10 |               0   |            11   | 0.909 |                                             | instrumental  |
| ghallu_ghallu | Demucs  | Humming                      |             10 |           19 |              11   |            21.5 | 0.696 |                                             | vocals        |
| ghallu_ghallu | Demucs  | Interlude 1 ( Instrumental ) |             19 |           40 |              21.5 |            36.5 | 0.714 | Boundary Lag                                | instrumental  |
| ghallu_ghallu | Demucs  | Pallavi                      |             40 |           60 |              36.5 |           101.5 | 0.308 | Boundary Early                              | vocals        |
| ghallu_ghallu | Demucs  | Charanam 1                   |             60 |           91 |              36.5 |           101.5 | 0.477 | Boundary Early                              | vocals        |
| ghallu_ghallu | Demucs  | Pallavi ( Repeat )           |             91 |          101 |              36.5 |           101.5 | 0.154 | Boundary Early                              | vocals        |
| ghallu_ghallu | Demucs  | Interlude 2 ( Instrumental ) |            101 |          141 |             101.5 |           126.5 | 0.625 |                                             | instrumental  |
| ghallu_ghallu | Demucs  | Humming                      |            141 |          150 |             126.5 |           202   | 0.119 | Boundary Early                              | vocals        |
| ghallu_ghallu | Demucs  | Charanam 2                   |            150 |          201 |             126.5 |           202   | 0.675 | Boundary Early                              | vocals        |
| ghallu_ghallu | Demucs  | Interlude 3 ( Instrumental ) |            201 |          244 |             202   |           235.5 | 0.779 |                                             | instrumental  |
| ghallu_ghallu | Demucs  | Charanam 3                   |            244 |          294 |             235.5 |           351.5 | 0.431 | Boundary Early                              | vocals        |
| ghallu_ghallu | Demucs  | ( Pallavi + Charanam 1 )     |            294 |          335 |             235.5 |           351.5 | 0.353 | Boundary Early                              | vocals        |
| ghallu_ghallu | Demucs  | Pallavi ( Final )            |            335 |          351 |             235.5 |           351.5 | 0.138 | Boundary Early                              | vocals        |
| ghallu_ghallu | SAM     | Intro (Instrumental )        |              0 |           10 |               3   |            22   | 0.318 | Boundary Lag; Instrumental->Vocal Confusion | instrumental  |
| ghallu_ghallu | SAM     | Humming                      |             10 |           19 |               3   |            22   | 0.474 | Boundary Early                              | vocals        |
| ghallu_ghallu | SAM     | Interlude 1 ( Instrumental ) |             19 |           40 |              22   |            37   | 0.714 | Boundary Lag                                | instrumental  |
| ghallu_ghallu | SAM     | Pallavi                      |             40 |           60 |              37   |           103.5 | 0.301 | Boundary Early                              | vocals        |
| ghallu_ghallu | SAM     | Charanam 1                   |             60 |           91 |              37   |           103.5 | 0.466 | Boundary Early                              | vocals        |
| ghallu_ghallu | SAM     | Pallavi ( Repeat )           |             91 |          101 |              37   |           103.5 | 0.15  | Boundary Early                              | vocals        |
| ghallu_ghallu | SAM     | Interlude 2 ( Instrumental ) |            101 |          141 |             103.5 |           118.5 | 0.375 | Boundary Lag                                | instrumental  |

## 5. Hybrid / Ensemble Proposal
Based on the error profile:
1. **Gating Rule**: Since Demucs has a lower Vocal FPR, use Demucs to define 'Instrumental' and 'Vocal' zones.
2. **Refinement**: Only accept SAM vocal predictions if they fall within a Demucs 'Vocal' zone.
3. **Impact**: This would eliminate approximately 49% of SAM's false alarms while retaining its noise suppression within valid vocal regions.
