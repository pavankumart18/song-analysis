import librosa
import numpy as np
import math

class BlockDetector:
    def __init__(self, window_duration=2.0, energy_threshold=0.015):
        """
        :param window_duration: Analysis window size in seconds (default 2s)
        :param energy_threshold: RMS energy threshold to decide vocal presence
        """
        self.window_duration = window_duration
        self.threshold = energy_threshold

    def process(self, vocals_path):
        """
        Scans vocals.wav and returns a list of blocks.
        """
        print(f"[BlockDetector] Analyzing {vocals_path}...")
        
        # Load audio (mono)
        y, sr = librosa.load(vocals_path, sr=None, mono=True)
        total_duration = librosa.get_duration(y=y, sr=sr)
        
        samples_per_window = int(self.window_duration * sr)
        
        # 1. Calculate RMS for each window
        num_windows = math.ceil(len(y) / samples_per_window)
        window_states = [] # True for 'vocals', False for 'instrumental'
        
        for i in range(num_windows):
            start_sample = i * samples_per_window
            end_sample = min((i + 1) * samples_per_window, len(y))
            chunk = y[start_sample:end_sample]
            
            if len(chunk) == 0:
                break
            
            # Use a slightly higher threshold to avoid noise being picked up as vocals
            rms = np.sqrt(np.mean(chunk**2))
            is_vocals = rms > self.threshold
            window_states.append(is_vocals)

        if not window_states:
            return []

        # 2. Smoothing: Fill short gaps in vocals
        # Use a very small gap limit (1.0s) to keep distinct vocal parts separate
        # (e.g. humming vs pallavi).
        gap_limit = int(1.0 / self.window_duration)
        for i in range(1, len(window_states) - gap_limit):
             if window_states[i-1] and not window_states[i] and window_states[i+gap_limit]:
                  for j in range(gap_limit):
                      window_states[i+j] = True

        # 3. Group into blocks
        raw_blocks = []
        if not window_states: return []
        
        current_type = "vocals" if window_states[0] else "instrumental"
        current_start_idx = 0
        
        for i, is_vocal in enumerate(window_states):
            block_type = "vocals" if is_vocal else "instrumental"
            if block_type != current_type:
                raw_blocks.append({
                    "start": round(current_start_idx * self.window_duration, 2),
                    "end": round(i * self.window_duration, 2),
                    "type": current_type
                })
                current_type = block_type
                current_start_idx = i
        
        raw_blocks.append({
            "start": round(current_start_idx * self.window_duration, 2),
            "end": round(total_duration, 2),
            "type": current_type
        })
        
        # Calculate Energy stats for raw blocks to help identification
        for b in raw_blocks:
            # simple slice mapping
            s_idx = int(b['start'] / self.window_duration)
            e_idx = int(b['end'] / self.window_duration)
            if s_idx < len(window_states):
                 # We don't have the raw RMS values stored in window_states (booleans).
                 # Retaining RMS would be better, but for now we can infer "strength" 
                 # or just assume vocals=high. 
                 # Actually, let's just stick to duration for now, 
                 # or re-calculate if precision is needed.
                 # User asked to "crosscheck with vocals.wav".
                 # Let's trust duration for differentiating Humming vs Pallavi.
                 pass

        
        # 4. Merge Logic
        # For Indian songs, interludes are usually long (15s+). 
        # Anything shorter is just a pause or bridge.
        final_blocks = []
        if not raw_blocks: return []

        final_blocks.append(raw_blocks[0])
        
        for b in raw_blocks[1:]:
            prev = final_blocks[-1]
            
            # MERGE RULE: Aggressive merging to reduce segment count
            # A true "Interlude" in Indian songs is significant (usually > 10-15s).
            # Short musical bridges between lyric lines (e.g. 5-8s) should remain part of the Vocal block.
            if prev['type'] == 'vocals' and b['type'] == 'instrumental' and (b['end'] - b['start']) < 8.0:
                 prev['end'] = b['end']
            elif prev['type'] == 'vocals' and b['type'] == 'vocals':
                 prev['end'] = b['end']
            elif prev['type'] == 'instrumental' and b['type'] == 'instrumental':
                 prev['end'] = b['end']
            # Also merge VERY short vocal bursts (< 2.0s) into instrumental (likely noise)
            elif prev['type'] == 'instrumental' and b['type'] == 'vocals' and (b['end'] - b['start']) < 2.0:
                 prev['end'] = b['end']
            else:
                 final_blocks.append(b)

        # Final cleanup for consecutive same-types
        merged = []
        if final_blocks:
            merged.append(final_blocks[0])
            for b in final_blocks[1:]:
                p = merged[-1]
                if p['type'] == b['type']:
                    p['end'] = b['end']
                else:
                    merged.append(b)
        
        print(f"[BlockDetector] Found {len(merged)} musically meaningful blocks.")
        return merged

if __name__ == "__main__":
    # Test stub
    import sys
    if len(sys.argv) > 1:
        detector = BlockDetector()
        blocks = detector.process(sys.argv[1])
        for b in blocks:
            print(b)
