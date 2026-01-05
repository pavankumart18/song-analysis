# Verification Report: Mari Antaga Svsc Movie

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
| 0 | **Intro** | 0.0 | 8.0 | 8.0 |
| 1 | **Pallavi** | 8.0 | 65.5 | 57.5 |
| 2 | **Interlude 1** | 65.5 | 82.5 | 17.0 |
| 3 | **Charanam 1** | 82.5 | 241.48 | 158.98 |

## 3. Verification & Comparison
- Compare the **LLM Estimated** 'Pallavi' start vs **Detected** 'Pallavi' start.
- Note: LLM estimates are often approximate (+/- 5-10s) whereas Detected timestamps are from the actual audio file.
