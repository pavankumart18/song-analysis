# Verification Report: Oh Sita Hey Rama

## 1. LLM Estimated Structure (Training Data / Knowledge)
| Label | Start (s) | End (s) |
| :--- | :--- | :--- |
| Intro | 0 | 30 |
| Pallavi | 30 | 75 |
| Interlude 1 | 75 | 105 |
| Charanam 1 | 105 | 150 |
| Interlude 2 | 150 | 180 |
| Charanam 2 | 180 | 225 |
| Outro | 225 | 255 |

## 2. Detected Segmentation (Audio Analysis)
| Index | Label | Start (s) | End (s) | Duration (s) |
| :--- | :--- | :--- | :--- | :--- |
| 0 | **Intro** | 0.0 | 17.5 | 17.5 |
| 1 | **Pallavi** | 17.5 | 120.0 | 102.5 |
| 2 | **Interlude 1** | 120.0 | 138.5 | 18.5 |
| 3 | **Charanam 1** | 138.5 | 160.5 | 22.0 |
| 4 | **Interlude 2** | 160.5 | 180.0 | 19.5 |
| 5 | **Charanam 2** | 180.0 | 215.0 | 35.0 |
| 6 | **Interlude 3** | 215.0 | 225.0 | 10.0 |
| 7 | **Outro** | 225.0 | 233.24 | 8.24 |

## 3. Verification & Comparison
- Compare the **LLM Estimated** 'Pallavi' start vs **Detected** 'Pallavi' start.
- Note: LLM estimates are often approximate (+/- 5-10s) whereas Detected timestamps are from the actual audio file.
