# /speak — Text-to-speech for command output

Run the TTS script to speak text aloud or save it to an MP3 file. Use alone with inline text or a file path, or after other commands (e.g. `/briefing`) to hear their summary as audio.

## Instructions

You are running the speak (TTS) command for Altamira Capital. Follow these steps.

### Step 1: Parse arguments

The user will provide arguments: **$ARGUMENTS**

Arguments can be:

- **Inline text** — Text in quotes to speak (e.g. `"Your daily briefing. S&P 500 is up 0.5 percent."`).
- **File path** — Path to a file whose contents should be spoken (e.g. `outputs/briefing-voice-2025-02-23.txt` or `outputs/briefing-2025-02-23.md`). Path is relative to the workspace root.
- **Shortcut: briefing** — If the user says `briefing`, `last briefing`, or `briefing audio`, treat as a request to speak the **Voice script** from the most recent briefing. Resolve as in Step 2.

Optional flags (if the user includes them):

- **Save to MP3** — e.g. `--out outputs/briefing-2025-02-23.mp3` or "save to file". Use `--out` when calling the script.
- **No playback** — If they only want to save an MP3 without speaking aloud, use `--no-speak` with `--out`.

If no arguments are provided, ask: "What should I speak? Provide text in quotes, a file path (e.g. outputs/briefing-voice-2025-02-23.txt), or say 'briefing' to speak the last briefing summary."

### Step 2: Resolve the text to speak

- **If arguments are inline text:** Use that text (with proper escaping for the shell when calling the script).
- **If arguments are a file path:** Use that path with `--file`. The script path is `scripts/speak_text.py`; the file path is relative to the workspace (e.g. `outputs/briefing-voice-2025-02-23.txt`).
- **If shortcut "briefing":**
  1. Look for the most recent voice-script file: `outputs/briefing-voice-*.txt` (by modification time). If found, use `--file path/to/briefing-voice-{DATE}.txt`.
  2. If not found, look for the most recent briefing report: `outputs/briefing-*.md`. Read it and extract the **Voice script** section (the paragraph labeled "Voice script" or "Read aloud" that is meant for TTS). Use that text with `--text "..."`.
  3. If no briefing report exists, say: "No briefing found. Run /briefing first, or provide text or a file path."

### Step 3: Run the speak script

From the workspace root, run:

```bash
python scripts/speak_text.py --text "<resolved text>"
```

or

```bash
python scripts/speak_text.py --file <path>
```

If the user asked to save to an MP3, add:

```bash
--out outputs/speak-{DATE}.mp3
```

(or a path they specified). To only save and not play aloud: add `--no-speak`.

**Examples:**

- Speak inline: `python scripts/speak_text.py --text "Your daily briefing. S&P 500 is up 0.5 percent."`
- Speak from file: `python scripts/speak_text.py --file outputs/briefing-voice-2025-02-23.txt`
- Speak briefing (from file or extracted from report): resolve per Step 2, then run with `--text` or `--file`.
- Save to MP3: `python scripts/speak_text.py --text "..." --out outputs/briefing-2025-02-23.mp3` (omit `--no-speak` to also play aloud).

### Step 4: Confirm in chat

After the script runs:

- If it spoke aloud: "Spoke the text aloud."
- If it saved a file: "Saved audio to &lt;path&gt;."
- If the script failed (e.g. missing pyttsx3 or edge-tts): report the error and suggest `pip install pyttsx3` for playback or `pip install edge-tts` for MP3.

## Combining with other commands

- **After /briefing:** Run `/speak briefing` to hear the briefing summary. You can also run `/briefing` and then in the same or next message say "speak it" or "run /speak briefing".
- **After /market-brief:** Run `/speak "&lt;paste the one- to two-sentence narrative from the brief&gt;"`.
- **After /moat or /analyze-ticker:** Run `/speak "&lt;paste the 2–4 sentence summary from the command output&gt;"` or save the summary to a file and run `/speak outputs/moat-summary.txt`.

## Context

- **Script:** `scripts/speak_text.py` — supports `--text`, `--file`, `--out` (MP3 via edge-tts), `--no-speak`, `--rate`, `--voice`.
- **Playback (speak aloud):** Uses `pyttsx3`. **MP3 (save to file):** Uses `edge-tts` when `--out` is set; use `--no-speak` to only save without playing.
- **Workspace root:** Commands run from the workspace root; paths like `outputs/` are relative to it.
