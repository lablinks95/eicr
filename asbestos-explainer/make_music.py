"""Synthesise a 30 s upbeat corporate background track (120 BPM, C-G-Am-F)."""
import numpy as np, wave, sys
SR = 44100; DUR = 30.0; BPM = 120; BEAT = 60 / BPM
N = int(SR * DUR); t = np.arange(N) / SR
mix = np.zeros((N, 2))
rng = np.random.default_rng(7)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR); j = min(N, i + len(sig))
    if i >= N: return
    s = sig[: j - i] * gain
    mix[i:j, 0] += s * np.sqrt(0.5 * (1 - pan)); mix[i:j, 1] += s * np.sqrt(0.5 * (1 + pan))
def env(n, a, r):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    return e * np.exp(-np.arange(n) / SR / r)
def lp(x, k):  # simple one-pole low-pass
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += k * (v - acc); y[i] = acc
    return y
# chords (MIDI) per bar: C, G, Am, F
chords = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
roots = [36, 43, 45, 41]
bars = int(DUR / (4 * BEAT))
for b in range(bars):
    c = chords[b % 4]; r = roots[b % 4]; t0 = b * 4 * BEAT
    # pad: detuned saws, filtered
    n = int(4 * BEAT * SR) + int(0.3 * SR); tt = np.arange(n) / SR
    pad = sum(((tt * hz(m) * d) % 1 * 2 - 1) for m in c for d in (0.997, 1.003))
    pad = lp(pad, 0.04) * np.minimum(1, np.minimum(tt / 0.25, (n / SR - tt) / 0.3))
    add(pad, t0, gain=0.035)
    # bass: root on each beat, eighth-note push
    for k in range(8):
        if k % 2 and b < 2: continue
        nn = int(BEAT / 2 * SR); tt = np.arange(nn) / SR
        s = np.sin(2 * np.pi * hz(r) * tt) + 0.3 * np.sin(4 * np.pi * hz(r) * tt)
        add(s * env(nn, 0.005, 0.18), t0 + k * BEAT / 2, gain=0.22)
    # pluck arpeggio 16ths
    if b >= 1:
        arp = [c[0] + 12, c[1] + 12, c[2] + 12, c[1] + 24]
        for k in range(16):
            nn = int(0.4 * SR); tt = np.arange(nn) / SR; f = hz(arp[k % 4])
            s = (np.sin(2*np.pi*f*tt) + 0.4*np.sin(4*np.pi*f*tt) + 0.15*np.sin(6*np.pi*f*tt)) * env(nn, 0.002, 0.09)
            add(s, t0 + k * BEAT / 4, pan=0.35 if k % 2 else -0.35, gain=0.07)
    # drums
    for k in range(4):
        bt = t0 + k * BEAT
        if b >= 1:  # kick
            nn = int(0.35 * SR); tt = np.arange(nn) / SR
            ph = 2 * np.pi * np.cumsum(50 + 110 * np.exp(-tt / 0.03)) / SR
            add(np.sin(ph) * env(nn, 0.001, 0.12), bt, gain=0.55)
        if b >= 3:  # offbeat hat
            nn = int(0.06 * SR); s = rng.standard_normal(nn); s = s - lp(s, 0.5)
            add(s * env(nn, 0.001, 0.015), bt + BEAT / 2, pan=0.2, gain=0.09)
        if b >= 5 and k in (1, 3):  # clap
            nn = int(0.2 * SR); s = rng.standard_normal(nn); s = s - lp(s, 0.15)
            add(s * env(nn, 0.001, 0.05), bt, gain=0.16)
# final ringing chord on the last bar boundary is covered by fade
fade_in = np.minimum(1, t / 0.4); fade_out = np.clip((DUR - t) / 2.5, 0, 1)
mix *= (fade_in * fade_out)[:, None]
mix = np.tanh(mix * 1.2); mix *= 0.7 / np.abs(mix).max()
out = (mix * 32767).astype(np.int16)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
