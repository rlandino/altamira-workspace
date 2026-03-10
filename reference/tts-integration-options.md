# Better TTS: GitHub Repos to Clone and Integrate

Use these repos to improve text-to-speech for the briefing (and other commands) beyond the current `pyttsx3` / `edge-tts` setup.

---

## 1. **Coqui TTS** (recommended for best quality)

- **Repo:** https://github.com/coqui-ai/TTS  
- **Stars:** ~44k | **License:** MPL-2.0  
- **Best for:** High-quality, natural-sounding speech; voice cloning; 1,100+ languages; XTTS v2 with streaming and low latency.

**Clone and install:**

```bash
cd X:\Claude\altamira-workspace
git clone https://github.com/coqui-ai/TTS.git repos/coqui-TTS
cd repos/coqui-TTS
pip install -e .
```

**Quick test (Python API):**

```python
from TTS.api import TTS
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
tts.tts_to_file(text="Your daily briefing. S&P 500 is up 0.45 percent.", file_path="output.wav")
```

**Integration with `speak_text.py`:** Add a Coqui backend that loads a small English model (e.g. `tts_models/en/ljspeech/glow-tts` or `tts_models/en/vctk/vits` for multi-speaker) and either plays via sounddevice/pyaudio or writes to a temp WAV and plays it. Prefer a single-speaker model for low latency.

**Requirements:** Python 3.9–3.11; PyTorch; ~2–4 GB disk for models. GPU optional but improves speed.

---

## 2. **RealtimeTTS** (multi-engine, streaming, drop-in style)

- **Repo:** https://github.com/KoljaB/RealtimeTTS  
- **Stars:** ~3.7k | **License:** Mixed (per-engine)  
- **Best for:** Multiple TTS engines (Edge, Coqui, OpenAI, Azure, Piper, System); streaming/low latency; fallback if one engine fails.

**Clone (optional) or pip:**

```bash
# Option A: pip only (no clone)
pip install realtimetts[edge]   # Edge TTS only (free, good quality)
pip install realtimetts[all]    # All engines (Coqui, Edge, Azure, etc.)

# Option B: clone for examples and custom engines
cd X:\Claude\altamira-workspace
git clone https://github.com/KoljaB/RealtimeTTS.git repos/RealtimeTTS
cd repos/RealtimeTTS
pip install -e ".[edge]"
```

**Quick test:**

```python
from RealtimeTTS import TextToAudioStream, EdgeEngine

engine = EdgeEngine(voice="en-US-GuyNeural")
stream = TextToAudioStream(engine)
stream.feed("Your daily briefing. S&P 500 is up 0.45 percent.")
stream.play()  # or stream.play_async()
```

**Integration with `speak_text.py`:** Use `EdgeEngine` (or `SystemEngine` for pyttsx3-like) and call `stream.feed(text)` then `stream.play()`. For file output use `stream.play(output_wavfile="path.wav", muted=True)` (see RealtimeTTS docs for exact param).

**Requirements:** Python 3.9–3.12; `portaudio` on Linux/macOS for playback. Edge engine needs internet; Coqui engine needs more disk/GPU.

---

## 3. **Summary**

| Repo           | Clone command                    | Use case                          |
|----------------|----------------------------------|-----------------------------------|
| **Coqui TTS**  | `git clone https://github.com/coqui-ai/TTS.git repos/coqui-TTS` | Best voice quality, local, many languages |
| **RealtimeTTS**| `git clone https://github.com/KoljaB/RealtimeTTS.git repos/RealtimeTTS` | Multi-engine, streaming, Edge/Coqui/System |

**Suggested path:**  
- For **better quality with minimal change:** keep `edge-tts` (or add **RealtimeTTS** with `EdgeEngine`) for a quick upgrade.  
- For **best quality and offline:** clone **Coqui TTS**, add a Coqui backend in `scripts/speak_text.py`, and optionally keep `edge-tts` as fallback when offline or when Coqui is not installed.

---

## 4. **Wiring into `speak_text.py`**

- Add an optional `--engine coqui` or `--engine edge` (default `pyttsx3` for offline, or `edge` if available).  
- If `realtimetts` is installed: `from RealtimeTTS import TextToAudioStream, EdgeEngine` and use `EdgeEngine` when `--engine edge`.  
- If Coqui TTS is installed (from cloned repo or `pip install TTS`): import `TTS.api.TTS`, load a small model once, and call `tts.tts_to_file(...)` or synthesize to a buffer and play with `sounddevice`/`pyaudio`.

See `scripts/speak_text.py` for current structure; add a `speak_coqui()` and `speak_realtime_edge()` and choose in `main()` based on `args.engine` or availability.
