import os
import librosa
import numpy as np
import soundfile as sf
from typing import Dict

# Paths to stems produced by Demucs (or similar)
VOCALS = "separated/htdemucs/dheera_dheera/vocals.mp3"
NONVOCALS = "separated/htdemucs/dheera_dheera/no_vocals.mp3"

# Output folders (one for each stem, aligned by the same vocal-driven boundaries)
OUT_VOCAL = "segments_vocals"
OUT_NONVOCAL = "segments_nonvocals"
os.makedirs(OUT_VOCAL, exist_ok=True)
os.makedirs(OUT_NONVOCAL, exist_ok=True)

# Load stems (use vocals to decide boundaries)
vocals, sr = librosa.load(VOCALS, sr=None)
nonvocals, _ = librosa.load(NONVOCALS, sr=sr)

# Segmentation parameters
frame_sec = 0.1
frame_len = int(frame_sec * sr)
THRESH_ON = 0.01    # start vocal when above this energy
THRESH_OFF = 0.007  # stop vocal when it falls below this (hysteresis)
SMOOTH_FRAMES = 5   # simple smoothing to avoid flicker from light signals

# Compute per-frame energy on vocals
energies = []
for i in range(0, len(vocals), frame_len):
    frame = vocals[i:i+frame_len]
    energy = np.sqrt(np.mean(frame**2)) if len(frame) else 0
    energies.append(energy)
energies = np.array(energies)

# Initial activity mask
active = energies > THRESH_ON

# Smooth the activity mask to suppress tiny blips
if SMOOTH_FRAMES > 1:
    window = np.ones(SMOOTH_FRAMES, dtype=int)
    conv = np.convolve(active.astype(int), window, mode="same")
    active = conv >= (SMOOTH_FRAMES // 2 + 1)

# Build segments using hysteresis
segments = []
in_active = False
start = 0
for idx, is_active in enumerate(active):
    frame_start = idx * frame_len
    frame_end = min((idx + 1) * frame_len, len(vocals))

    if not in_active and is_active:
        start = frame_start
        in_active = True
    elif in_active:
        if energies[idx] < THRESH_OFF and not is_active:
            segments.append((start, frame_start))
            in_active = False

# Close any trailing segment
if in_active:
    segments.append((start, len(vocals)))

# Write aligned segments for both stems
for idx, (s, e) in enumerate(segments, 1):
    vocal_audio = vocals[s:e]
    nonv_audio = nonvocals[s:e]

    out_v = f"{OUT_VOCAL}/segment_{idx:03d}_vocal.mp3"
    out_nv = f"{OUT_NONVOCAL}/segment_{idx:03d}_nonvocal.mp3"

    sf.write(out_v, vocal_audio, sr)
    sf.write(out_nv, nonv_audio, sr)

    print(f"Written: {out_v} and {out_nv}")

# Reconstruct continuous stems and full mix using detected boundaries
recon_v = np.zeros_like(vocals)
for s, e in segments:
    recon_v[s:e] = vocals[s:e]

# Keep full non-vocals so music is not muted during vocal gaps
recon_nv = nonvocals.copy()

mix = recon_v + recon_nv
# Simple normalization to avoid clipping
peak = np.max(np.abs(mix))
if peak > 1.0:
    mix = mix / peak

sf.write("reconstructed_vocals.mp3", recon_v, sr)
sf.write("reconstructed_nonvocals.mp3", recon_nv, sr)
sf.write("reconstructed_mix.mp3", mix, sr)

print("Written: reconstructed_vocals.mp3, reconstructed_nonvocals.mp3, reconstructed_mix.mp3")

# Also provide a direct sum of stems (no gating/segmentation); should be closest to original
direct_mix = vocals + nonvocals
peak_direct = np.max(np.abs(direct_mix))
if peak_direct > 1.0:
    direct_mix = direct_mix / peak_direct
sf.write("direct_mix.mp3", direct_mix, sr)
print("Written: direct_mix.mp3 (raw stem sum, no segmentation)")


def compare_signals(reference: np.ndarray, test: np.ndarray) -> Dict[str, float]:
    """
    Compare two mono signals with simple, fast metrics.
    - MAE / RMSE capture average error
    - SNR (dB) shows how loud the error is vs. the reference
    - Pearson correlation captures shape similarity
    """
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

    # Avoid NaNs when signals are constant
    ref_std = np.std(ref)
    tst_std = np.std(tst)
    if ref_std > 0 and tst_std > 0:
        corr = float(np.corrcoef(ref, tst)[0, 1])
    else:
        corr = 1.0 if np.allclose(ref, tst) else 0.0

    return {"mae": mae, "rmse": rmse, "snr_db": snr_db, "corr": corr}


# Compare the reconstructed mix to the direct stem sum
metrics = compare_signals(direct_mix, mix)
print(
    "Comparison (direct_mix vs reconstructed_mix): "
    f"MAE={metrics['mae']:.6f}, RMSE={metrics['rmse']:.6f}, "
    f"SNR={metrics['snr_db']:.2f} dB, Corr={metrics['corr']:.4f}"
)
