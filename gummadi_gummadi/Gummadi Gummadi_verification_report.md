# Verification Report: Gummadi Gummadi

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
| 0 | **Intro** | 0.0 | 11.5 | 11.5 |
| 1 | **Pallavi** | 11.5 | 104.0 | 92.5 |
| 2 | **Interlude 1** | 104.0 | 121.0 | 17.0 |
| 3 | **Charanam 1** | 121.0 | 172.5 | 51.5 |
| 4 | **Interlude 2** | 172.5 | 204.5 | 32.0 |
| 5 | **Charanam 2** | 204.5 | 277.0 | 72.5 |
| 6 | **Outro** | 277.0 | 290.5 | 13.5 |

## 3. Verification & Comparison
- Compare the **LLM Estimated** 'Pallavi' start vs **Detected** 'Pallavi' start.
- Note: LLM estimates are often approximate (+/- 5-10s) whereas Detected timestamps are from the actual audio file.
