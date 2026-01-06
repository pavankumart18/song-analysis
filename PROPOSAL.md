# Hybrid Segmentation Proposal

Based on the quantitative analysis of Demucs vs SAM, the following hybrid (ensemble) logic is proposed to maximize segmentation accuracy.

## 1. Problem Statement
*   **Demucs**: High boundaries precision, good at ignoring background instrumentals, but sometimes misses soft vocal starts (higher Deletion rate).
*   **SAM**: Extremely sensitive, captures almost all vocal activity, but suffers from high **Instrumental Confusion** (e.g., classifying violins or flutes as vocals), resulting in a high False Positive Rate (~49%).

## 2. Evidence Metrics
*   **Mean IoU**: Demucs (~0.42) > SAM (~0.26)
*   **Vocal False Positive Rate**: Demucs (~20%) < SAM (~49%)
*   **Conclusion**: SAM cannot be trusted alone for structural segmentation due to hallucinations, but it is useful for detecting subtle vocals that Demucs might miss *if constrained*.

## 3. Proposed Logic: "The Gated Ensemble"

We propose a **Gating Mechanism** where Demucs acts as the primary structure definer, and SAM acts as a refined detailer *within* safe zones.

### Rule 1: The Trust Zone (Demucs Anchor)
*   **Logic**: If Demucs predicts a vocal segment, we accept it as the "Base Truth".
*   **Refinement**: We look at the SAM prediction *overlapping* this Demucs segment.
    *   If SAM's start time is *slightly* earlier (within 2s) than Demucs, we extend the start time to match SAM (capturing the breath/onset).
    *   If SAM's end time is later, we extend the end time.
*   **Benefit**: Combines Demucs' reliability with SAM's fine-grained onset detection.

### Rule 2: The Suppression Zone (Instrumental Guard)
*   **Logic**: If SAM predicts a vocal segment BUT Demucs explicitly predicts an "Instrumental" segment (or no vocal segment) at that same time:
*   **Action**: **REJECT** the SAM segment.
*   **Reasoning**: This eliminates the ~49% false positives caused by instrumental confusion. The probability of Demucs *completely* missing a vocal section is lower than the probability of SAM hallucinating one.

### Rule 3: The Recovery Zone (Weak Signals)
*   **Logic**: If SAM predicts a high-confidence segment (long duration > 5s) and Demucs predicts *nothing* (silence):
*   **Action**: Flag for **Manual Review** or accept with "Low Confidence" tag.
*   **Reasoning**: This covers distinct acapella or very soft humming sections that Demucs might miss.

## 4. Implementation Algorithm (Python Pseudo-Code)

```python
def ensemble_segments(demucs_segs, sam_segs):
    final_segments = []
    
    # 1. Start with Demucs
    for d_seg in demucs_segs:
        # Find overlapping SAM segments
        overlaps = find_overlaps(d_seg, sam_segs)
        
        if overlaps:
            # Merge boundaries: take min(start) and max(end) of the cluster
            # This captures the full extent of the vocalization
            new_start = min(d_seg.start, min([s.start for s in overlaps]))
            new_end = max(d_seg.end, max([s.end for s in overlaps]))
            final_segments.append(Segment(new_start, new_end, "vocals"))
        else:
            # Keep Demucs as is
            final_segments.append(d_seg)
            
    # 2. Handle SAM-only segments (The "Recovery" or "Suppression" decision)
    for s_seg in sam_segs:
        if not is_overlapping_any(s_seg, demucs_segs):
            # Check length constraint to filter short noise
            if s_seg.duration > 3.0: 
                # Optional: Add as "Potential Vocal"
                final_segments.append(Segment(s_seg.start, s_seg.end, "potential_vocals"))
                
    return merge_nearby_segments(final_segments, threshold=0.5)
```
