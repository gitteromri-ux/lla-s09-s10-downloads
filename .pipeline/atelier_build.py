#!/usr/bin/env python3
"""Atelier final build: pace edit + grade normalization + brand cards + music.

Consumes the 28 rendered Seedance chunks (.pipeline/final_chunk_urls.json),
retimes each to its exact driver window (15s x26, 8s, 9s), normalizes the
grade across chunks, cuts the Atelier WIDE<->TIGHT rhythm, splices the navy
brand cards at 0 / 90 / 210 / 330 / 402, and muxes monologue + music bed.
Output: out/<OUT>.mp4
"""
import json, os, subprocess, sys, tempfile

OUT = os.environ.get("OUT", "Courtney_CINEMA_FINAL_0717")
FPS = 30
W, H = 1920, 1080
CARDS = "production/cards/png/horizontal"
ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
       "-pix_fmt", "yuv420p", "-an"]

def run(*cmd):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)

def ffdur(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, check=True)
    return float(p.stdout.strip())

urls = json.load(open(".pipeline/final_chunk_urls.json"))
assert len(urls) == 28
DUR = [15.0] * 26 + [8.0, 9.0]

os.makedirs("chunks", exist_ok=True)
os.makedirs("seg", exist_ok=True)
os.makedirs("out", exist_ok=True)

# 1) download + retime to driver window
for i, u in enumerate(urls):
    c, r = f"chunks/c_{i:02d}.mp4", f"chunks/r_{i:02d}.mp4"
    if not os.path.exists(c):
        run("curl", "-sS", "-L", "--fail", "--retry", "4", "--retry-delay", "3", u, "-o", c)
    f = DUR[i] / ffdur(c)
    run("ffmpeg", "-y", "-loglevel", "error", "-i", c,
        "-vf", f"setpts=PTS*{f:.8f},fps={FPS}", "-t", str(DUR[i]), *ENC, r)

# 2) measure mean luma per chunk (3 frames each) -> per-chunk eq params
from PIL import Image
import glob

def mean_luma(path, dur):
    vals = []
    for t in (dur * 0.2, dur * 0.5, dur * 0.8):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
            fn = tf.name
        run("ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}",
            "-i", path, "-frames:v", "1", fn)
        im = Image.open(fn).convert("L").resize((160, 90))
        px = list(im.getdata())
        vals.append(sum(px) / len(px))
        os.unlink(fn)
    return sum(vals) / len(vals)

luma = [mean_luma(f"chunks/r_{i:02d}.mp4", DUR[i]) for i in range(28)]
targetA = sum(luma[i] for i in range(0, 28, 2)) / 14.0
print("lumas:", [round(v, 1) for v in luma], "targetA:", round(targetA, 1))

def eqfilter(i):
    delta = max(-0.10, min(0.10, (targetA - luma[i]) / 255.0 * 0.9))
    sat = 1.05 if i % 2 else 1.0            # B chunks slightly duller
    return f"eq=brightness={delta:.4f}:saturation={sat}"

# 3) crop geometries
WIDE = None
TIGHT = f"crop=1113:626:403:119,scale={W}:{H}:flags=lanczos"
MT1  = f"crop=1420:799:250:11,scale={W}:{H}:flags=lanczos"
MT2  = f"crop=1267:713:326:54,scale={W}:{H}:flags=lanczos"

def cutplan(i):
    d = DUR[i]
    if i % 2 == 0:                            # A / wide master
        if i == 0:   return [(2.4, 5.0, WIDE), (5.0, 10.0, TIGHT), (10.0, 15.0, WIDE)]
        if i in (6, 14, 22):                  # brand card replaces first 2.8s
            return [(2.8, 8.0, TIGHT), (8.0, 15.0, WIDE)]
        if i == 26:  return [(0.0, 4.0, WIDE), (4.0, 8.0, TIGHT)]
        return [(0.0, 5.0, WIDE), (5.0, 10.0, TIGHT), (10.0, 15.0, WIDE)]
    else:                                     # B master: stay tight, hide set
        if i == 27:  return [(0.0, 4.0, MT1)]  # end card covers 402->tail
        return [(0.0, 7.5, MT1), (7.5, 15.0, MT2)]

def cardclip(png, length, dst, fade_in=0.25, fade_out=0.25):
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=#0E1F48,"
          f"fade=t=in:st=0:d={fade_in},fade=t=out:st={max(0, length - fade_out):.2f}:d={fade_out},fps={FPS}")
    run("ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", f"{length:.2f}",
        "-i", png, "-vf", vf, *ENC, dst)

AD = ffdur("deliverables/audio_full_0717.m4a")
print("audio duration:", AD)

segments = []
# opener card (brand lockup on navy)
cardclip(f"{CARDS}/end_h.png", 2.4, "seg/s_open.mp4", fade_in=0.0)
segments.append("seg/s_open.mp4")

CARD_AT = {6: "cta1_h.png", 14: "cta2_h.png", 22: "cta3_h.png"}
for i in range(28):
    if i in CARD_AT:
        dst = f"seg/s_{i:02d}_card.mp4"
        cardclip(f"{CARDS}/{CARD_AT[i]}", 2.8, dst)
        segments.append(dst)
    for k, (a, b, crop) in enumerate(cutplan(i)):
        dst = f"seg/s_{i:02d}_{k}.mp4"
        vf = ",".join(x for x in (crop, eqfilter(i)) if x)
        run("ffmpeg", "-y", "-loglevel", "error",
            "-ss", f"{a:.2f}", "-t", f"{b - a:.2f}", "-i", f"chunks/r_{i:02d}.mp4",
            "-vf", vf if vf else "null", *ENC, dst)
        segments.append(dst)

# end card holds from t=402 to end of audio (+0.5s), fades in
end_len = max(3.0, AD - 402.0 + 0.5)
cardclip(f"{CARDS}/end_h.png", end_len, "seg/s_end.mp4", fade_in=0.4, fade_out=0.0)
segments.append("seg/s_end.mp4")

with open("list.txt", "w") as f:
    for s in segments:
        f.write(f"file '{os.path.abspath(s)}'\n")

r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", "list.txt", "-c", "copy", "out/video.mp4"])
if r.returncode != 0:
    run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
        "-i", "list.txt", *ENC[:-1], "out/video.mp4")
VD = ffdur("out/video.mp4")
print("video duration:", VD)

# 4) audio: monologue + music bed from t=0, gentle tail fade
run("ffmpeg", "-y", "-loglevel", "error",
    "-i", "deliverables/audio_full_0717.m4a",
    "-stream_loop", "-1", "-i", "assets/music_bed_0717.mp3",
    "-filter_complex",
    f"[1:a]volume=0.16[m];[0:a][m]amix=inputs=2:duration=first:normalize=0,"
    f"afade=t=out:st={AD - 2.5:.2f}:d=2.5[a]",
    "-map", "[a]", "-c:a", "aac", "-b:a", "256k", "out/audio.m4a")

run("ffmpeg", "-y", "-loglevel", "error", "-i", "out/video.mp4", "-i", "out/audio.m4a",
    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy",
    "-shortest", "-movflags", "+faststart", f"out/{OUT}.mp4")
run("ffprobe", "-v", "error", "-show_entries", "format=duration,size",
    "-of", "default=noprint_wrappers=1", f"out/{OUT}.mp4")

os.makedirs("deliverables/qc_cinema", exist_ok=True)
for p in (1, 30, 60, 91, 120, 150, 180, 211, 240, 270, 300, 331, 360, 390, 400, 404):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(p),
                    "-i", f"out/{OUT}.mp4", "-frames:v", "1",
                    f"deliverables/qc_cinema/at_{p}.jpg"])
print("BUILD OK")
