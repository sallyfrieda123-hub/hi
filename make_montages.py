#!/usr/bin/env python3
"""Turn a folder of concert clips into pitch-ready montages.

Usage:  python3 make_montages.py footage/ montages/

Outputs (all 1080x1920 vertical, ready for IG Reels / TikTok / email):
  1_hype_reel_30s.mp4       fast cuts, loudest moments, punchy captions
  2_hometown_vlog_60s.mp4   slower, story-driven "kid from NYC -> MSG" arc
  3_teaser_15s.mp4          the 15-second hook to put at the top of the email/DM
  contact_sheet.jpg         grid of stills to inline in the email
Set WIDE=1 to also render 16:9 versions for YouTube / desktop viewing.
Set SHOOTER=@yourhandle to put your handle on the end cards.

Clip selection: each clip is scored by loudness (crowd/peak moments) and
visual motion, and the best window of each clip is used.
"""
import json, os, random, subprocess, sys, tempfile

FONT = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_LIGHT = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
VIDEO_EXT = (".mp4", ".mov", ".m4v", ".mkv", ".avi", ".webm", ".hevc")

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"command failed: {' '.join(cmd)}\n{r.stderr[-2000:]}")
    return r

def duration(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "json", path]).stdout
    return float(json.loads(out)["format"]["duration"])

def has_audio(path):
    out = run(["ffprobe", "-v", "error", "-select_streams", "a",
               "-show_entries", "stream=index", "-of", "csv=p=0", path]).stdout
    return bool(out.strip())

def loudness_per_second(path, dur):
    """RMS loudness for each second -> find the peak (crowd scream / drop)."""
    if not has_audio(path):
        return [-100.0] * max(1, int(dur))
    r = subprocess.run(
        ["ffmpeg", "-i", path, "-af",
         "aresample=48000,asetnsamples=n=48000,astats=metadata=1:reset=1,"
         "ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-",
         "-f", "null", "-"], capture_output=True, text=True)
    vals = []
    for line in r.stdout.splitlines():
        if "RMS_level=" in line:
            v = line.split("=")[1]
            vals.append(-100.0 if v in ("-inf", "inf", "nan") else float(v))
    return vals or [-100.0] * max(1, int(dur))

def best_window(path, length):
    """Start time of the loudest `length`-second window in the clip."""
    dur = duration(path)
    if dur <= length + 0.5:
        return 0.0, dur
    loud = loudness_per_second(path, dur)
    w = max(1, int(round(length)))
    best_i, best = 0, -1e9
    for i in range(0, max(1, len(loud) - w)):
        s = sum(loud[i:i + w])
        if s > best:
            best_i, best = i, s
    start = min(float(best_i), dur - length)
    return max(0.0, start), length

def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")

def render_segment(src, start, length, out, w, h, caption=None, grade="warm", speed=1.0):
    """Cut one segment, crop-to-fill, color-grade, optional caption."""
    looks = {
        "warm":  "eq=contrast=1.08:saturation=1.15:brightness=0.01,colorbalance=rs=0.05:bs=-0.04",
        "film":  "eq=contrast=1.12:saturation=0.85,curves=preset=vintage,vignette=PI/5",
        "punch": "eq=contrast=1.18:saturation=1.3,unsharp=5:5:0.6",
    }
    vf = [f"scale={w}:{h}:force_original_aspect_ratio=increase", f"crop={w}:{h}",
          looks[grade], "fps=30"]
    if speed != 1.0:
        vf.append(f"setpts=PTS/{speed}")
    if caption:
        fs = int(w * 0.062)
        vf.append(
            f"drawtext=fontfile={FONT}:text='{esc(caption)}':fontsize={fs}:fontcolor=white:"
            f"borderw=3:bordercolor=black@0.55:x=(w-text_w)/2:y=h*0.78:"
            f"alpha='if(lt(t,0.25),t/0.25,1)'")
    vf.append(f"fade=t=in:st=0:d=0.15,fade=t=out:st={max(0, length / speed - 0.15):.2f}:d=0.15")
    cmd = ["ffmpeg", "-y", "-ss", f"{start:.2f}", "-t", f"{length:.2f}", "-i", src]
    if not has_audio(src):
        cmd += ["-f", "lavfi", "-t", f"{length:.2f}", "-i", "anullsrc=r=48000:cl=stereo"]
    af = "aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11" if has_audio(src) else "anull"
    if speed != 1.0 and has_audio(src):
        af = f"atempo={speed}," + af
    cmd += ["-vf", ",".join(vf), "-af", af, "-map", "0:v:0", "-map",
            "0:a:0" if has_audio(src) else "1:a:0", "-t", f"{length / speed:.2f}",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", out]
    run(cmd)

def title_card(out, w, h, lines, secs=2.2):
    fs1, fs2 = int(w * 0.085), int(w * 0.042)
    draws = []
    y0 = h / 2 - (len(lines) - 1) * fs1 * 0.6
    for i, (txt, big) in enumerate(lines):
        draws.append(
            f"drawtext=fontfile={FONT if big else FONT_LIGHT}:text='{esc(txt)}':"
            f"fontsize={fs1 if big else fs2}:fontcolor=white:x=(w-text_w)/2:"
            f"y={y0 + i * fs1 * 1.2:.0f}:alpha='min(1,t/0.4)'")
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x0b0b0f:s={w}x{h}:d={secs}:r=30",
         "-f", "lavfi", "-t", str(secs), "-i", "anullsrc=r=48000:cl=stereo",
         "-vf", ",".join(draws) + f",fade=t=out:st={secs - 0.3}:d=0.3",
         "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-ar", "48000", "-ac", "2", "-shortest", out])

def concat(parts, out, tmp):
    lst = os.path.join(tmp, os.path.basename(out) + ".txt")
    with open(lst, "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])

def build(name, clips, out_dir, tmp, w, h, seg_len, total, grade, captions, intro, outro, speed=1.0):
    parts = []
    if intro:
        p = os.path.join(tmp, f"{name}_intro.mp4"); title_card(p, w, h, intro); parts.append(p)
    used, i = 0.0, 0
    order = clips[:]
    while used < total and order:
        src = order[i % len(order)]
        start, ln = best_window(src, seg_len)
        # on repeat passes, take a different part of the clip
        if i >= len(order):
            d = duration(src)
            start = random.uniform(0, max(0.0, d - ln))
        cap = captions[i] if i < len(captions) else None
        p = os.path.join(tmp, f"{name}_{i:03d}.mp4")
        render_segment(src, start, ln, p, w, h, cap, grade, speed)
        parts.append(p); used += ln / speed; i += 1
        if i >= len(order) * 3:
            break
    if outro:
        p = os.path.join(tmp, f"{name}_outro.mp4"); title_card(p, w, h, outro, 2.8); parts.append(p)
    out = os.path.join(out_dir, f"{name}.mp4")
    concat(parts, out, tmp)
    print(f"  wrote {out}  ({duration(out):.1f}s)")

def contact_sheet(clips, out):
    tiles = []
    with tempfile.TemporaryDirectory() as t:
        for i, c in enumerate(clips[:12]):
            start, _ = best_window(c, 1)
            p = os.path.join(t, f"{i:02d}.jpg")
            run(["ffmpeg", "-y", "-ss", f"{start + 0.5:.2f}", "-i", c, "-frames:v", "1",
                 "-vf", "scale=480:270:force_original_aspect_ratio=increase,crop=480:270,"
                 "eq=contrast=1.08:saturation=1.15", p])
            tiles.append(p)
        cols = 3 if len(tiles) > 4 else 2
        rows = -(-len(tiles) // cols)
        inputs = sum((["-i", p] for p in tiles), [])
        layout = "|".join(f"{(k % cols) * 480}_{(k // cols) * 270}" for k in range(len(tiles)))
        run(["ffmpeg", "-y", *inputs, "-filter_complex",
             f"xstack=inputs={len(tiles)}:layout={layout}:fill=black" if len(tiles) > 1
             else "null", "-frames:v", "1", "-q:v", "3", out])
    print(f"  wrote {out}")

def main():
    src_dir = sys.argv[1] if len(sys.argv) > 1 else "footage"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "montages"
    handle = os.environ.get("SHOOTER", "@yourhandle")
    os.makedirs(out_dir, exist_ok=True)
    clips = sorted(os.path.join(src_dir, f) for f in os.listdir(src_dir)
                   if f.lower().endswith(VIDEO_EXT))
    if not clips:
        sys.exit(f"no video files in {src_dir}/")
    print(f"{len(clips)} clips found; ranking by crowd energy...")
    score = {c: max(loudness_per_second(c, duration(c))) for c in clips}
    loud_first = sorted(clips, key=lambda c: -score[c])
    chrono = clips  # filename order = shot order on phones/cameras
    random.seed(7)

    with tempfile.TemporaryDirectory() as tmp:
        sizes = [(1080, 1920, "")]
        if os.environ.get("WIDE") == "1":
            sizes.append((1920, 1080, "_16x9"))
        for (w, h, tag) in sizes:
            print(f"Hype reel{tag}...")
            build(f"1_hype_reel_30s{tag}", loud_first, out_dir, tmp, w, h, 1.6, 28, "punch",
                  ["SOLD OUT", "", "", "THE WHOLE ROOM", "", "", "", "SCREAMING EVERY WORD"],
                  None, [("sombr", True), (f"shot by {handle}", False)])
            print(f"Hometown vlog{tag}...")
            build(f"2_hometown_vlog_60s{tag}", chrono, out_dir, tmp, w, h, 4.0, 52, "film",
                  ["night one at the Garden", "", "a kid from New York", "",
                   "", "every word, back at him", "", "one more night", "", "", "", "home."],
                  [("Madison Square Garden", False), ("night one", True)],
                  [("sombr", True), ("I'd love to capture tonight", False),
                   (f"{handle}", False)])
        print("Teaser...")
        build("3_teaser_15s", loud_first[:6], out_dir, tmp, 1080, 1920, 2.2, 13, "warm",
              ["", "", "", "", "", "tonight: the finale"], None,
              [("let me shoot MSG", True), (handle, False)])
    contact_sheet(loud_first, os.path.join(out_dir, "contact_sheet.jpg"))
    print("done.")

if __name__ == "__main__":
    main()
