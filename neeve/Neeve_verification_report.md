# Verification Report: Neeve

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
| 0 | **Intro** | 0.0 | 8.5 | 8.5 |
| 1 | **Pallavi** | 8.5 | 97.0 | 88.5 |
| 2 | **Interlude 1** | 97.0 | 111.0 | 14.0 |
| 3 | **Charanam 1** | 111.0 | 281.54 | 170.54 |

## 3. Verification & Comparison
- Compare the **LLM Estimated** 'Pallavi' start vs **Detected** 'Pallavi' start.
- Note: LLM estimates are often approximate (+/- 5-10s) whereas Detected timestamps are from the actual audio file.
