# Verification Report: Manava Manava

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
| 0 | **Intro** | 0.0 | 3.5 | 3.5 |
| 1 | **Pallavi** | 3.5 | 84.0 | 80.5 |
| 2 | **Interlude 1** | 84.0 | 99.5 | 15.5 |
| 3 | **Charanam 1** | 99.5 | 193.5 | 94.0 |
| 4 | **Interlude 2** | 193.5 | 212.5 | 19.0 |
| 5 | **Bridge** | 212.5 | 214.5 | 2.0 |
| 6 | **Interlude 3** | 214.5 | 245.5 | 31.0 |
| 7 | **Charanam 2** | 245.5 | 337.08 | 91.58 |

## 3. Verification & Comparison
- Compare the **LLM Estimated** 'Pallavi' start vs **Detected** 'Pallavi' start.
- Note: LLM estimates are often approximate (+/- 5-10s) whereas Detected timestamps are from the actual audio file.
