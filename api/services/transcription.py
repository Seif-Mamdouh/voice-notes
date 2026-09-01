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


class TranscriptionService:
    """Orchestrates transcription: speech-to-text provider + persistence.

    Deps are injected (repo has a production default) so tests can fake both
    without a DB or network. The production transcriber is wired in at the
    composition root (routers/transcriptions.py).
    """

    def __init__(
        self,
        transcriber: Transcriber,
        repo: TranscriptionRepo | None = None,
    ):
        self._transcriber = transcriber
        self._repo = repo or TranscriptionRepo()

    async def create(self, audio: bytes, mimetype: str) -> Transcription:
        result = await self._transcriber.transcribe(audio, mimetype)
        return self._repo.add(result.transcript, result.duration_seconds)

    def list(self) -> list[Transcription]:
        return self._repo.list()

    def get(self, transcription_id: int) -> Transcription | None:
        return self._repo.get(transcription_id)
