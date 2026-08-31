from dataclasses import dataclass
from typing import Protocol

from models import Transcription
from repos.transcriptions import TranscriptionRepo


@dataclass
class TranscriptResult:
    transcript: str
    duration_seconds: float | None


class Transcriber(Protocol):
    async def transcribe(self, audio: bytes, mimetype: str) -> TranscriptResult: ...


class StubTranscriber:
    """Placeholder transcriber until the Deepgram client lands."""

    async def transcribe(self, audio: bytes, mimetype: str) -> TranscriptResult:
        return TranscriptResult(
            transcript=f"[stub transcript for {len(audio)} bytes of {mimetype}]",
            duration_seconds=None,
        )


class TranscriptionService:
    """Orchestrates transcription: speech-to-text provider + persistence.

    Deps are injected with production defaults so tests can fake both
    without a DB or network.
    """

    def __init__(
        self,
        transcriber: Transcriber | None = None,
        repo: TranscriptionRepo | None = None,
    ):
        self._transcriber = transcriber or StubTranscriber()
        self._repo = repo or TranscriptionRepo()

    async def create(self, audio: bytes, mimetype: str) -> Transcription:
        result = await self._transcriber.transcribe(audio, mimetype)
        return self._repo.add(result.transcript, result.duration_seconds)

    def list(self) -> list[Transcription]:
        return self._repo.list()

    def get(self, transcription_id: int) -> Transcription | None:
        return self._repo.get(transcription_id)
