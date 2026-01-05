import librosa
import numpy as np
import math

class BlockDetector:
    def __init__(self, window_duration=0.5, energy_threshold=0.015):
        """
        :param window_duration: Analysis window size in seconds (default 0.5s)
        :param energy_threshold: RMS energy threshold to decide vocal presence
        """
        self.window_duration = window_duration
        self.threshold = energy_threshold

    def calculate_chroma_signature(self, y, sr):
        """
        Calculates a 12-dimensional chroma vector representing the melodic signature.
        """
        try:
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr, n_chroma=12)
            # Average over time to get global key/mode signature
            return np.mean(chroma, axis=1).tolist()
        except:
            return None

    def process(self, vocals_path, is_sam=False):
        """
        Scans vocals.wav and returns a list of blocks with multi-feature analysis AND Melodic Signatures.
        """
        print(f"[BlockDetector] Analyzing {vocals_path} (SAM Mode: {is_sam})...")
        
        # Load audio (mono)
        y, sr = librosa.load(vocals_path, sr=None, mono=True)
        total_duration = librosa.get_duration(y=y, sr=sr)
        
        # Calculate sample parameters
        samples_per_window = int(self.window_duration * sr)
        hop_length = samples_per_window
        
        # --- Feature Extraction ---
        # 1. RMS Energy
        S = librosa.magphase(librosa.stft(y, hop_length=hop_length, window='rect', n_fft=2048))[0]
        rms_frames_high_res = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
        
        # 2. Spectral Features
        hop_std = 512
        cent_frames = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_std)[0]
        flat_frames = librosa.feature.spectral_flatness(y=y, hop_length=hop_std)[0]
        zcr_frames = librosa.feature.zero_crossing_rate(y, hop_length=hop_std)[0]
        voiced_probs = 1 - flat_frames

        # Mapping frames to windows
        frames_per_window = int(samples_per_window / hop_std)
        num_windows = math.ceil(len(y) / samples_per_window)
        
        # --- Stem Quality Assessment (SAM Check) ---
        stem_quality = "acceptable"
        if is_sam:
            avg_global_flatness = np.mean(flat_frames)
            if avg_global_flatness > 0.4: 
                stem_quality = "noisy"
                print(f"[BlockDetector] SAM Stem classified as NOISY (Flatness: {avg_global_flatness:.2f})")
        
        window_states = [] 
        window_features = []
        
        for i in range(num_windows):
            start_frame = i * frames_per_window
            end_frame = min((i+1) * frames_per_window, len(rms_frames_high_res))
            
            # Aggregate stats
            w_rms = np.mean(rms_frames_high_res[start_frame:end_frame]) if start_frame < end_frame else 0
            w_cent = np.mean(cent_frames[start_frame:end_frame]) if start_frame < end_frame else 0
            w_flat = np.mean(flat_frames[start_frame:end_frame]) if start_frame < end_frame else 0
            w_zcr = np.mean(zcr_frames[start_frame:end_frame]) if start_frame < end_frame else 0
            w_voiced_prob = np.mean(voiced_probs[start_frame:end_frame]) if start_frame < end_frame else 0
            w_has_pitch = w_voiced_prob > 0.3 
            
            # --- Dynamic Thresholding ---
            current_threshold = self.threshold
            if stem_quality == "noisy":
                current_threshold *= 1.5 
            
            # --- Multi-Feature Decision Rule ---
            is_vocal = False
            if w_has_pitch:
                if w_rms > (current_threshold * 0.5): is_vocal = True
            else:
                if w_rms > current_threshold:
                     if 300 < w_cent < 3500 and w_flat < 0.2: is_vocal = True

            window_features.append({
                "rms": float(w_rms),
                "pitch_prob": float(w_voiced_prob),
                "is_vocal": is_vocal
            })
            window_states.append(is_vocal)


        # --- 2. Smoothing ---
        gap_limit = int(1.0 / self.window_duration)
        for i in range(1, len(window_states) - gap_limit):
             if window_states[i-1] and not window_states[i] and window_states[i+gap_limit]:
                  for j in range(gap_limit):
                      window_states[i+j] = True
                      
        # --- 3. Grouping into Blocks with Melody Extraction ---
        raw_blocks = []
        if not window_states: return []
        
        current_type = "vocals" if window_states[0] else "instrumental"
        current_start_idx = 0
        
        def finalize_block(idx_start, idx_end, b_type):
            start_t = round(idx_start * self.window_duration, 2)
            end_t = round(idx_end * self.window_duration, 2)
            
            # Aggregate standard stats
            f_slice = window_features[idx_start:idx_end]
            avg_rms = np.mean([f['rms'] for f in f_slice]) if f_slice else 0
            avg_pitch = np.mean([f['pitch_prob'] for f in f_slice]) if f_slice else 0
            
            melodic_signature = None
            if b_type == "vocals" and (end_t - start_t) > 2.0:
                 # Extract Melody Signature (Chroma) for comparison later
                 # Slice audio directly (expensive but necessary for patterning)
                 s_samp = int(start_t * sr)
                 e_samp = int(end_t * sr)
                 if e_samp > len(y): e_samp = len(y)
                 melodic_signature = self.calculate_chroma_signature(y[s_samp:e_samp], sr)

            return {
                "start": start_t,
                "end": end_t,
                "type": b_type,
                "avg_rms": float(avg_rms),
                "avg_pitch_prob": float(avg_pitch),
                "is_melodic": bool(avg_pitch > 0.4),
                "melodic_signature": melodic_signature # New!
            }

        for i, is_vocal in enumerate(window_states):
            block_type = "vocals" if is_vocal else "instrumental"
            if block_type != current_type:
                raw_blocks.append(finalize_block(current_start_idx, i, current_type))
                current_type = block_type
                current_start_idx = i
        
        raw_blocks.append(finalize_block(current_start_idx, len(window_states), current_type))
        
        # --- 4. Merge Logic ---
        final_blocks = []
        if not raw_blocks: return []
        final_blocks.append(raw_blocks[0])
        
        for b in raw_blocks[1:]:
            prev = final_blocks[-1]
            merged = False
            
            # 1. Merge same types
            if prev['type'] == b['type']:
                prev['end'] = b['end']
                prev['avg_pitch_prob'] = (prev['avg_pitch_prob'] + b['avg_pitch_prob']) / 2
                # If merging two vocal blocks, we lose the individual melody signatures.
                # In v2, we should re-compute signature on merge. For now, keep the larger one or None.
                merged = True
            
            # 2. Short Instrumental Gaps
            elif prev['type'] == 'vocals' and b['type'] == 'instrumental':
                 merge_limit = 6.0
                 if stem_quality == "noisy": merge_limit = 3.0
                 if (b['end'] - b['start']) < merge_limit:
                     prev['end'] = b['end']
                     merged = True
            
            # 3. Very short Vocal bursts
            elif prev['type'] == 'instrumental' and b['type'] == 'vocals':
                 dur = b['end'] - b['start']
                 if dur < 0.8 and not b['is_melodic']: 
                     prev['end'] = b['end']
                     merged = True
                     
            if not merged:
                final_blocks.append(b)
                
        # Final Pass
        clean_blocks = []
        if final_blocks:
            clean_blocks.append(final_blocks[0])
            for b in final_blocks[1:]:
                p = clean_blocks[-1]
                if p['type'] == b['type']:
                    p['end'] = b['end']
                else:
                    clean_blocks.append(b)
        
        # --- 5. Similarity Check (Structure Proof) ---
        # Find repeating vocal blocks (Pallavi Candidates)
        # We add a "repeats" flag to help the LLM!
        vocal_blocks = [b for b in clean_blocks if b['type'] == 'vocals' and b['melodic_signature']]
        
        for i, b1 in enumerate(vocal_blocks):
            for b2 in vocal_blocks[i+1:]:
                 # Cosine similarity of chroma vectors
                 sig1 = np.array(b1['melodic_signature'])
                 sig2 = np.array(b2['melodic_signature'])
                 
                 similarity = np.dot(sig1, sig2) / (np.linalg.norm(sig1) * np.linalg.norm(sig2))
                 
                 if similarity > 0.85: # High similarity threshold
                     b1['repeats'] = True
                     b2['repeats'] = True
                     print(f"[Melody] Similarity found ({similarity:.2f}) between {b1['start']}s and {b2['start']}s")

        print(f"[BlockDetector] Found {len(clean_blocks)} musically meaningful blocks (Multi-Feature + Melody).")
        return clean_blocks

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        detector = BlockDetector()
        blocks = detector.process(sys.argv[1])
        for b in blocks:
            print(b)
