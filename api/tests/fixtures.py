"""Fakes for the service seam — no DB, no network."""

from models import Transcription
from services.transcription import Transcribe, TranscriptResult


def fake_transcribe(result: TranscriptResult) -> tuple[Transcribe, list[tuple[bytes, str]]]:
    calls: list[tuple[bytes, str]] = []

    async def transcribe(audio: bytes, mimetype: str) -> TranscriptResult:
        calls.append((audio, mimetype))
        return result

    return transcribe, calls


class FakeRepo:
    """In-memory stand-in for TranscriptionRepo."""

    def __init__(self):
        self.rows: list[Transcription] = []

    def add(self, transcript: str, duration_seconds: float | None) -> Transcription:
        row = Transcription(transcript=transcript, duration_seconds=duration_seconds)
        row.id = len(self.rows) + 1
        self.rows.append(row)
        return row

    def list(self) -> list[Transcription]:
        return list(reversed(self.rows))

    def get(self, transcription_id: int) -> Transcription | None:
        return next((r for r in self.rows if r.id == transcription_id), None)
