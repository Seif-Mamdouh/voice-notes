from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from models import Transcription
from repos.transcriptions import TranscriptionRepo


@dataclass
class TranscriptResult:
    transcript: str
    duration_seconds: float | None


type Transcribe = Callable[[bytes, str], Awaitable[TranscriptResult]]


async def create(
    audio: bytes,
    mimetype: str,
    *,
    transcribe: Transcribe,
    repo: TranscriptionRepo | None = None,
) -> Transcription:
    """Speech-to-text then persist. transcribe/repo are injected so tests can fake both."""
    result = await transcribe(audio, mimetype)
    return (repo or TranscriptionRepo()).add(result.transcript, result.duration_seconds)


def list_all(repo: TranscriptionRepo | None = None) -> list[Transcription]:
    return (repo or TranscriptionRepo()).list()


def get(transcription_id: int, repo: TranscriptionRepo | None = None) -> Transcription | None:
    return (repo or TranscriptionRepo()).get(transcription_id)
