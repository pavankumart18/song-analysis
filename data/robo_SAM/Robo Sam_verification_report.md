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
| 0 | **Intro (Instrumental)** | 0.0 | 1.5 | 1.5 |
| 1 | **Humming / Alaap** | 1.5 | 2.0 | 0.5 |
| 2 | **Intro (Instrumental)** | 2.0 | 11.5 | 9.5 |
| 3 | **Pallavi** | 11.5 | 30.5 | 19.0 |
| 4 | **Interlude 1** | 30.5 | 40.0 | 9.5 |
| 5 | **Charanam 1** | 40.0 | 317.0 | 277.0 |

## 3. Verification & Comparison
- Compare the **LLM Estimated** 'Pallavi' start vs **Detected** 'Pallavi' start.
- Note: LLM estimates are often approximate (+/- 5-10s) whereas Detected timestamps are from the actual audio file.
