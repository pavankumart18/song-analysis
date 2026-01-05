# Verification Report: Robo Sam

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
| 0 | **Intro** | 0.0 | 11.0 | 11.0 |
| 1 | **Pallavi** | 11.0 | 28.0 | 17.0 |
| 2 | **Interlude 1** | 28.0 | 39.0 | 11.0 |
| 3 | **Charanam 1** | 39.0 | 209.5 | 170.5 |
| 4 | **Interlude 2** | 209.5 | 226.5 | 17.0 |
| 5 | **Charanam 2** | 226.5 | 316.8 | 90.3 |

## 3. Verification & Comparison
- Compare the **LLM Estimated** 'Pallavi' start vs **Detected** 'Pallavi' start.
- Note: LLM estimates are often approximate (+/- 5-10s) whereas Detected timestamps are from the actual audio file.
