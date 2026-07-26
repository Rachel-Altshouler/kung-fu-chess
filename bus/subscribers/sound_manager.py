from __future__ import annotations

import math
import struct
import threading
import wave
from pathlib import Path

from bus.event_bus import EventBus
from bus.event_types import Events


def _sounds_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "assets" / "sounds"


def _write_tone_wav(
    path: Path,
    freqs: tuple[float, ...],
    duration_sec: float,
    volume: float = 0.18,
    sample_rate: int = 22050,
):
    n_samples = int(sample_rate * duration_sec)
    frames = bytearray()
    for i in range(n_samples):
        t = i / sample_rate
        fade_in = min(t / 0.008, 1.0)
        fade_out = max(0.0, min(1.0, (duration_sec - t) / 0.05))
        env = fade_in * fade_out * math.exp(-2.2 * t)
        sample = 0.0
        for idx, f in enumerate(freqs):
            amp = 1.0 / (idx + 1)
            sample += amp * math.sin(2 * math.pi * f * t)
        sample /= max(sum(1.0 / (i + 1) for i in range(len(freqs))), 1)
        sample = int(max(-1.0, min(1.0, sample * volume * env)) * 32767)
        frames.extend(struct.pack("<h", sample))

    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(bytes(frames))


def ensure_sound_assets() -> dict[str, Path]:
    sounds = _sounds_dir()
    assets = {
        "move": sounds / "move_soft.wav",
        "capture": sounds / "capture_soft.wav",
    }
    if not assets["move"].is_file():
        _write_tone_wav(
            assets["move"],
            freqs=(523.25, 659.25),
            duration_sec=0.11,
            volume=0.16,
        )
    if not assets["capture"].is_file():
        _write_tone_wav(
            assets["capture"],
            freqs=(392.0, 523.25, 659.25),
            duration_sec=0.16,
            volume=0.18,
        )
    return assets


class SoundManager:
    """Move/capture SFX via winsound only — never opens an extra window."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.last_sound = None
        self._assets = ensure_sound_assets() if enabled else {}
        self._lock = threading.Lock()

    def subscribe(self, bus: EventBus):
        bus.subscribe(Events.PIECE_MOVED, self.on_piece_moved)
        bus.subscribe(Events.PIECE_CAPTURED, self.on_piece_captured)

    def start_background(self):
        return

    def stop_background(self):
        return

    def on_piece_moved(self, data):
        self._play_sfx("move")

    def on_piece_captured(self, data):
        self._play_sfx("capture")

    def on_game_started(self, data):
        return

    def on_game_ended(self, data):
        return

    def _play_sfx(self, name: str):
        self.last_sound = name
        if not self.enabled:
            return
        path = self._assets.get(name)
        if path is None:
            return

        def _run():
            with self._lock:
                try:
                    import winsound

                    winsound.PlaySound(
                        str(path),
                        winsound.SND_FILENAME | winsound.SND_ASYNC,
                    )
                except Exception:
                    pass

        threading.Thread(target=_run, daemon=True).start()
