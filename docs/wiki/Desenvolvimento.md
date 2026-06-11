# Desenvolvimento

Stack: CustomTkinter, yt-dlp, FFmpeg, Demucs, faster-whisper, edge-tts, PyInstaller

```bash
PYTHONPATH=src python3 src/presentation/main.py
python3 -m pytest tests/ -v
ruff check src/ tests/
python3 -m PyInstaller scripts/AudioLabEditor.spec --log-level WARN
```
