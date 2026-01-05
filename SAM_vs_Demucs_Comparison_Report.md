# SAM vs Demucs: Comparative Analysis Report

This report compares the performance of SAM (Segment Anything Model) vs Demucs (HTDemucs) on 8 Indian songs.

# Source Separation Model Performance Evaluation

## Executive Summary

After evaluating the performance of SAM (Segment Anything Model) and Demucs (HTDemucs Hybrid Transformer) across 8 songs, Demucs emerges as the overall winner. Demucs consistently provided more realistic song structures with better alignment to expected musical sections, despite occasionally misclassifying humming or breathing as vocals. SAM, while effective in some cases, often over-segmented due to its reliance on visual/spectrogram masks, leading to less coherent song structures.

## Song-by-Song Analysis

### 1. Ghallu Ghallu
**SAM**: Over-segmented the song, with a long vocal section labeled as instrumental.
**Demucs**: Provided a more coherent structure, though it included humming as vocals. The segmentation was more aligned with expected song sections.
**Winner**: Demucs

### 2. Mari Antaga SVSC Movie
**SAM**: Provided a simpler structure with fewer segments, but missed some instrumental sections.
**Demucs**: Offered a detailed segmentation, capturing multiple interludes and charanams, though it initially misclassified the intro as vocals.
**Winner**: Demucs

### 3. Naa Autograph Sweet Memories
**SAM**: Segmented the song into more sections, but the transitions were abrupt.
**Demucs**: Merged sections more effectively, providing a smoother transition between vocals and instrumentals.
**Winner**: Demucs

### 4. Narasimha - Narasimha
**SAM**: Over-simplified the structure, missing instrumental interludes.
**Demucs**: Captured a detailed structure with clear interludes and charanams, providing a realistic song flow.
**Winner**: Demucs

### 5. Narasimha Yekku Tholi Mettu
**SAM**: Simplified the structure, missing key instrumental sections.
**Demucs**: Accurately identified interludes and charanams, offering a comprehensive song structure.
**Winner**: Demucs

### 6. Oh Sita Hey Rama
**SAM**: Provided a detailed segmentation but included unnecessary interludes.
**Demucs**: Offered a more concise structure, though it extended some instrumental sections.
**Winner**: Demucs

### 7. Pilichina Ranantava Song With
**SAM**: Both models performed similarly, with minor differences in segment boundaries.
**Demucs**: Slightly better alignment with expected song structure.
**Winner**: Demucs

### 8. Raja Edo Oka Ragam
**SAM**: Over-simplified the structure, missing charanams.
**Demucs**: Captured a detailed structure with clear transitions between sections.
**Winner**: Demucs

### 9. Nuvvostanante Nenoddantana
**SAM**: Provided a coherent structure but missed some instrumental sections.
**Demucs**: Offered a more detailed segmentation, capturing all key sections.
**Winner**: Demucs

### 10. Robo
**SAM**: Over-segmented the song, leading to an incoherent structure.
**Demucs**: Provided a more realistic segmentation, though it merged some sections.
**Winner**: Demucs

## Conclusion

Demucs is recommended for future use in identifying song structures, as it consistently provides more realistic and coherent segmentations. While SAM can be useful in certain scenarios, its tendency to over-segment due to noise makes it less reliable for this task. Future improvements could focus on refining Demucs' ability to distinguish between vocals and non-vocal sounds like humming or breathing.