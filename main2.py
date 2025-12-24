import os
import librosa
import numpy as np
import soundfile as sf

# -----------------------
# INPUT FILES (Demucs output)
# -----------------------
VOCALS = "separated/htdemucs/dheera_dheera/vocals.mp3"
NONVOCALS = "separated/htdemucs/dheera_dheera/no_vocals.mp3"

OUT_DIR = "segments"
os.makedirs(OUT_DIR, exist_ok=True)

# -----------------------
# LOAD AUDIO
# -----------------------
vocals, sr = librosa.load(VOCALS, sr=None)
nonvocals, _ = librosa.load(NONVOCALS, sr=sr)

length = min(len(vocals), len(nonvocals))
vocals = vocals[:length]
nonvocals = nonvocals[:length]

# -----------------------
# SEGMENTATION PARAMETERS
# -----------------------
FRAME_SEC = 0.1            # 100 ms
FRAME_LEN = int(FRAME_SEC * sr)

THRESH = 0.01              # minimum energy to be considered active
SMOOTH_FRAMES = 5          # suppress flicker

# -----------------------
# COMPUTE ENERGY PER FRAME
# -----------------------
v_energy = []
nv_energy = []

for i in range(0, length, FRAME_LEN):
    v = vocals[i:i+FRAME_LEN]
    nv = nonvocals[i:i+FRAME_LEN]

    v_energy.append(np.sqrt(np.mean(v**2)) if len(v) else 0)
    nv_energy.append(np.sqrt(np.mean(nv**2)) if len(nv) else 0)

v_energy = np.array(v_energy)
nv_energy = np.array(nv_energy)

# -----------------------
# DECIDE DOMINANT STATE
# -----------------------
states = []
for ve, ne in zip(v_energy, nv_energy):
    if ve > THRESH and ve > ne:
        states.append("vocal")
    elif ne > THRESH:
        states.append("instrumental")
    else:
        states.append(None)

# -----------------------
# SMOOTH STATES (majority vote)
# -----------------------
if SMOOTH_FRAMES > 1:
    smooth_states = []
    for i in range(len(states)):
        window = states[max(0, i-SMOOTH_FRAMES): i+SMOOTH_FRAMES+1]
        window = [s for s in window if s is not None]
        smooth_states.append(max(set(window), key=window.count) if window else None)
    states = smooth_states

# -----------------------
# BUILD SEGMENTS (ALTERNATING)
# -----------------------
segments = []
current = None
start_frame = 0

for i, state in enumerate(states):
    if state is None:
        state = current  # hold previous

    if current is None:
        current = state
        start_frame = i
    elif state != current:
        segments.append((current, start_frame, i))
        start_frame = i
        current = state

segments.append((current, start_frame, len(states)))

# -----------------------
# WRITE AUDIO SEGMENTS
# -----------------------
for idx, (label, s_f, e_f) in enumerate(segments, 1):
    s = s_f * FRAME_LEN
    e = min(e_f * FRAME_LEN, length)

    audio = vocals[s:e] + nonvocals[s:e]

    out = f"{OUT_DIR}/segment_{idx:03d}_{label}.mp3"
    sf.write(out, audio, sr)
    print("Written:", out)
