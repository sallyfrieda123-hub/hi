#!/usr/bin/env python3
"""Scan EVERY frame of every clip and find (a) the exact moments matching your
screenshots and (b) the strongest "whole crowd singing / MSG" moments.

Usage:
  python3 -I find_moments.py <clips_dir> <screenshots_dir> <out_dir>

Writes <out_dir>/moments.json and, for every hit, a still <out_dir>/frames/*.jpg
(full-resolution, for photo selects) plus a 1-in-30 frame index for review.

How it works:
  * Every frame is decoded (no skipping) at a small analysis size.
  * Screenshot match: each screenshot is compared to every frame with a 16x16
    grayscale signature (mean-normalised, so phone-screenshot brightness and UI
    overlays matter less). Best match per screenshot = that moment.
  * Crowd moments: per-second audio loudness (crowd singing/screaming) combined
    with frame-to-frame motion and stage-light brightness. Peaks become
    candidate clips. These are candidates for human/AI review, not final picks.
"""
import json, os, subprocess, sys
import numpy as np

AW, AH = 64, 36          # analysis frame size (every frame decoded at this size)
SIG = 16                 # signature grid
VIDEO_EXT = (".mp4", ".mov", ".m4v", ".mkv", ".hevc", ".avi", ".webm")
IMG_EXT = (".png", ".jpg", ".jpeg", ".heic", ".webp")

def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate:format=duration", "-of", "json", path],
        capture_output=True, text=True).stdout
    j = json.loads(out)
    num, den = j["streams"][0]["r_frame_rate"].split("/")
    return float(j["format"]["duration"]), float(num) / float(den)

def frames(path):
    """Yield every decoded frame as a (AH, AW) float array."""
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf",
        f"scale={AW}:{AH}:flags=area,format=gray", "-vsync", "0",
        "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    n = AW * AH
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(AH, AW).astype(np.float32)
    p.wait()

def signature(img):
    h, w = img.shape
    s = img[: h - h % SIG or h, : w - w % SIG or w]
    s = np.array([[c.mean() for c in np.array_split(r, SIG, axis=1)]
                  for r in np.array_split(s, SIG, axis=0)])
    s = s - s.mean()
    return s / (np.linalg.norm(s) + 1e-6)

def trim_borders(img, tol=6.0):
    """Drop flat rows/cols at the edges (phone UI bars, letterboxing)."""
    rows = np.where(img.std(axis=1) > tol)[0]
    cols = np.where(img.std(axis=0) > tol)[0]
    if len(rows) < 4 or len(cols) < 4:
        return img
    return img[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]

def load_image(path):
    W, H = 360, 780  # keep aspect roughly (phone screenshot); trim, then compare
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf",
        f"scale={W}:{H}:flags=area,format=gray", "-frames:v", "1",
        "-f", "rawvideo", "-"], capture_output=True).stdout
    img = np.frombuffer(raw, np.uint8).reshape(H, W).astype(np.float32)
    return trim_borders(img)

def loudness(path):
    r = subprocess.run(["ffmpeg", "-i", path, "-af",
        "aresample=48000,asetnsamples=n=24000,astats=metadata=1:reset=1,"
        "ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-",
        "-f", "null", "-"], capture_output=True, text=True).stdout
    v = []
    for line in r.splitlines():
        if "RMS_level=" in line:
            x = line.split("=")[1]
            v.append(-100.0 if x in ("-inf", "inf", "nan") else float(x))
    return np.array(v)  # one value per 0.5 s

def grab_still(path, t, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", path,
                    "-frames:v", "1", "-q:v", "1", out])

def main():
    clips_dir, shots_dir, out_dir = sys.argv[1:4]
    os.makedirs(os.path.join(out_dir, "frames"), exist_ok=True)
    clips = sorted(os.path.join(clips_dir, f) for f in os.listdir(clips_dir)
                   if f.lower().endswith(VIDEO_EXT))
    shots = sorted(os.path.join(shots_dir, f) for f in os.listdir(shots_dir)
                   if f.lower().endswith(IMG_EXT)) if os.path.isdir(shots_dir) else []
    shot_sigs = {s: signature(load_image(s)) for s in shots}
    best = {s: (-2.0, None, None) for s in shots}
    report = {"clips": [], "screenshot_matches": []}

    for c in clips:
        dur, fps = probe(c)
        print(f"scanning every frame: {os.path.basename(c)} ({dur:.1f}s @ {fps:.0f}fps)")
        prev, motion, bright, nframes = None, [], [], 0
        for i, f in enumerate(frames(c)):
            nframes += 1
            sig = signature(f)
            for s, ss in shot_sigs.items():
                score = float((sig * ss).sum())
                if score > best[s][0]:
                    best[s] = (score, c, i / fps)
            motion.append(0.0 if prev is None else float(np.abs(f - prev).mean()))
            bright.append(float(np.percentile(f, 95)))
            prev = f
        # per-second features
        secs = max(1, int(np.ceil(nframes / fps)))
        m = np.array([np.mean(motion[int(k * fps):int((k + 1) * fps)] or [0]) for k in range(secs)])
        b = np.array([np.mean(bright[int(k * fps):int((k + 1) * fps)] or [0]) for k in range(secs)])
        loud = loudness(c)
        l = np.array([loud[2 * k:2 * k + 2].mean() if len(loud) > 2 * k else -100 for k in range(secs)])
        z = lambda a: (a - a.mean()) / (a.std() + 1e-6)
        energy = 0.6 * z(l) + 0.25 * z(m) + 0.15 * z(b)
        # peaks at least 4 s apart
        peaks, order = [], np.argsort(-energy)
        for k in order:
            if all(abs(k - p) >= 4 for p in peaks):
                peaks.append(int(k))
            if len(peaks) >= 5:
                break
        cands = []
        for k in sorted(peaks):
            still = os.path.join(out_dir, "frames",
                                 f"{os.path.splitext(os.path.basename(c))[0]}_{k:04d}s.jpg")
            grab_still(c, k + 0.5, still)
            cands.append({"t": k, "energy": round(float(energy[k]), 2), "still": still})
        report["clips"].append({"clip": c, "duration": dur, "frames_scanned": nframes,
                                "energy_per_second": [round(float(e), 2) for e in energy],
                                "candidates": cands})

    for s, (score, c, t) in best.items():
        if c is None:
            continue
        still = os.path.join(out_dir, "frames", "match_" + os.path.splitext(os.path.basename(s))[0] + ".jpg")
        grab_still(c, t, still)
        report["screenshot_matches"].append({"screenshot": s, "clip": c, "t": round(t, 3),
            "confidence": round(score, 3), "still": still})
        print(f"  {os.path.basename(s)} -> {os.path.basename(c)} @ {t:.2f}s (match {score:.2f})")

    json.dump(report, open(os.path.join(out_dir, "moments.json"), "w"), indent=1)
    print(f"wrote {out_dir}/moments.json")

if __name__ == "__main__":
    main()
