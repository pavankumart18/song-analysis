import os
import librosa
import numpy as np
import soundfile as sf
import warnings
import glob

# Suppress warnings
warnings.filterwarnings("ignore")

def compare_signals(reference: np.ndarray, test: np.ndarray) -> dict:
    min_len = min(len(reference), len(test))
    if min_len == 0:
        return {"mae": np.nan, "rmse": np.nan, "snr_db": np.nan, "corr": np.nan}

    ref = reference[:min_len]
    tst = test[:min_len]
    diff = ref - tst

    mae = float(np.mean(np.abs(diff)))
    rmse = float(np.sqrt(np.mean(diff ** 2)))

    noise_power = np.mean(diff ** 2) + 1e-12
    signal_power = np.mean(ref ** 2) + 1e-12
    snr_db = float(10 * np.log10(signal_power / noise_power))

    ref_std = np.std(ref)
    tst_std = np.std(tst)
    if ref_std > 0 and tst_std > 0:
        corr = float(np.corrcoef(ref, tst)[0, 1])
    else:
        corr = 1.0 if np.allclose(ref, tst) else 0.0

    return {"mae": mae, "rmse": rmse, "snr_db": snr_db, "corr": corr}

def process_song_folder(folder_path):
    print(f"Analyzing in {folder_path}...")
    
    # Locate split files
    # Expected: separated/htdemucs/song/vocals.[mp3|wav]
    base_split = os.path.join(folder_path, "separated", "htdemucs", "song")
    
    # Try wav then mp3
    vocals_path = os.path.join(base_split, "vocals.wav")
    if not os.path.exists(vocals_path):
         vocals_path = os.path.join(base_split, "vocals.mp3")
    
    novocals_path = os.path.join(base_split, "no_vocals.wav")
    if not os.path.exists(novocals_path):
         novocals_path = os.path.join(base_split, "no_vocals.mp3")
         
    if not os.path.exists(vocals_path) or not os.path.exists(novocals_path):
        print(f"Separated files not found in {base_split}. Skipping reconstruction for this song.")
        return

    # Output folders
    OUT_VOCAL = os.path.join(folder_path, "segments_vocals")
    OUT_NONVOCAL = os.path.join(folder_path, "segments_nonvocals")
    os.makedirs(OUT_VOCAL, exist_ok=True)
    os.makedirs(OUT_NONVOCAL, exist_ok=True)

    # Load stems
    print(f"Loading audio from {vocals_path}...")
    try:
        vocals, sr = librosa.load(vocals_path, sr=None)
        nonvocals, _ = librosa.load(novocals_path, sr=sr)
    except Exception as e:
        print(f"Error loading audio: {e}")
        return

    # Segmentation parameters
    frame_sec = 0.1
    frame_len = int(frame_sec * sr)
    THRESH_ON = 0.01
    THRESH_OFF = 0.007
    SMOOTH_FRAMES = 5

    # Compute energy
    energies = []
    for i in range(0, len(vocals), frame_len):
        frame = vocals[i:i+frame_len]
        energy = np.sqrt(np.mean(frame**2)) if len(frame) else 0
        energies.append(energy)
    energies = np.array(energies)

    active = energies > THRESH_ON

    if SMOOTH_FRAMES > 1:
        window = np.ones(SMOOTH_FRAMES, dtype=int)
        conv = np.convolve(active.astype(int), window, mode="same")
        active = conv >= (SMOOTH_FRAMES // 2 + 1)

    segments = []
    in_active = False
    start = 0
    for idx, is_active in enumerate(active):
        frame_start = idx * frame_len
        if not in_active and is_active:
            start = frame_start
            in_active = True
        elif in_active:
             if energies[idx] < THRESH_OFF and not is_active:
                 segments.append((start, frame_start))
                 in_active = False
    if in_active:
        segments.append((start, len(vocals)))

    print(f"Found {len(segments)} segments.")

    for idx, (s, e) in enumerate(segments, 1):
        vocal_audio = vocals[s:e]
        nonv_audio = nonvocals[s:e]
        out_v = os.path.join(OUT_VOCAL, f"segment_{idx:03d}_vocal.mp3")
        out_nv = os.path.join(OUT_NONVOCAL, f"segment_{idx:03d}_nonvocal.mp3")
        sf.write(out_v, vocal_audio, sr)
        sf.write(out_nv, nonv_audio, sr)

    # Reconstruction
    recon_v = np.zeros_like(vocals)
    for s, e in segments:
        recon_v[s:e] = vocals[s:e]
    
    recon_nv = nonvocals.copy()
    mix = recon_v + recon_nv
    peak = np.max(np.abs(mix))
    if peak > 1.0: mix /= peak
    
    sf.write(os.path.join(folder_path, "reconstructed_vocals.mp3"), recon_v, sr)
    sf.write(os.path.join(folder_path, "reconstructed_nonvocals.mp3"), recon_nv, sr)
    sf.write(os.path.join(folder_path, "reconstructed_mix.mp3"), mix, sr)

    direct_mix = vocals + nonvocals
    peak_d = np.max(np.abs(direct_mix))
    if peak_d > 1.0: direct_mix /= peak_d
    sf.write(os.path.join(folder_path, "direct_mix.mp3"), direct_mix, sr)
    
    # Metrics
    metrics = compare_signals(direct_mix, mix)
    print(f"Metrics | MAE: {metrics['mae']:.6f}, SNR: {metrics['snr_db']:.2f} dB, Corr: {metrics['corr']:.4f}")

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    for item in os.listdir(root_dir):
        path = os.path.join(root_dir, item)
        if os.path.isdir(path) and os.path.exists(os.path.join(path, "song.mp3")):
            process_song_folder(path)

if __name__ == "__main__":
    main()
