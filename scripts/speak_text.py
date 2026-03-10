#!/usr/bin/env python3
"""
Text-to-speech for command summaries (e.g. briefing, market-brief).
Speak text aloud using pyttsx3 (offline) or save to MP3 using edge-tts.
Usage:
  python scripts/speak_text.py --text "Your summary here"
  python scripts/speak_text.py --file path/to/summary.txt
  python scripts/speak_text.py --file path/to/summary.txt --out outputs/briefing-2025-02-23.mp3
  echo "Your summary" | python scripts/speak_text.py
"""

import argparse
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"


def get_text(args: argparse.Namespace) -> str:
    if args.text:
        return args.text.strip()
    if args.file:
        path = Path(args.file)
        if not path.is_absolute():
            path = WORKSPACE / path
        return path.read_text(encoding="utf-8", errors="replace").strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    return ""


def speak_pyttsx3(text: str, rate: int = 150) -> None:
    """Speak using pyttsx3 (offline, no API key)."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", min(200, max(100, rate)))
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[speak_text] pyttsx3 failed: {e}", file=sys.stderr)
        raise


def save_edge_tts(text: str, out_path: Path, voice: str = "en-US-GuyNeural") -> None:
    """Save speech to MP3 using edge-tts (requires: pip install edge-tts)."""
    import asyncio
    try:
        import edge_tts
    except ImportError:
        print("[speak_text] edge-tts not installed. Run: pip install edge-tts", file=sys.stderr)
        raise
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    async def _generate():
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(str(out_path))

    asyncio.run(_generate())
    print(f"[speak_text] Saved {out_path}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Speak text aloud (TTS) or save to MP3 for command summaries."
    )
    parser.add_argument("--text", default=None, help="Text to speak")
    parser.add_argument("--file", default=None, help="Path to file containing text to speak")
    parser.add_argument(
        "--out",
        default=None,
        help="Save audio to this path (e.g. outputs/briefing-2025-02-23.mp3). Uses edge-tts.",
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=150,
        help="Speech rate for pyttsx3 (default 150). Ignored when using --out.",
    )
    parser.add_argument(
        "--voice",
        default="en-US-GuyNeural",
        help="Voice for edge-tts when using --out (default en-US-GuyNeural).",
    )
    parser.add_argument(
        "--no-speak",
        action="store_true",
        help="Only save to --out; do not speak aloud (useful when --out is set).",
    )
    args = parser.parse_args()

    text = get_text(args)
    if not text:
        print("[speak_text] No text provided. Use --text, --file, or stdin.", file=sys.stderr)
        sys.exit(1)

    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = WORKSPACE / out_path
        save_edge_tts(text, out_path, voice=args.voice)
    if not args.no_speak and not args.out:
        speak_pyttsx3(text, rate=args.rate)
    elif not args.no_speak and args.out:
        # User asked for both: save and speak (pyttsx3 for immediate playback)
        speak_pyttsx3(text, rate=args.rate)


if __name__ == "__main__":
    main()
