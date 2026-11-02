# Asbestos Survey Explainer (30 s)

Vertical 1080×1920 explainer for Shorts / Reels / TikTok. Navy & orange, animated text, synthesised background music.

- `asbestos-survey-explainer.mp4`: the finished video
- `explainer.html`: the animation (open it in a browser for a looping live preview)
- `render_frames.js`: renders 900 frames at 30 fps with Playwright
- `make_music.py`: generates the 120 BPM background track (royalty-free, made from code)

Rebuild:
```bash
node render_frames.js frames 30 4
python3 make_music.py music.wav
ffmpeg -framerate 30 -i frames/f_%04d.png -i music.wav -c:v libx264 -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -shortest -movflags +faststart asbestos-survey-explainer.mp4
```
