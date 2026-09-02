import mimetypes
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path

from models import Transcription
from repos.transcriptions import TranscriptionRepo

UPLOADS_DIR = Path("uploads")


@dataclass
class TranscriptResult:
    transcript: str
    duration_seconds: float | None
    summary: str | None = None


type Transcribe = Callable[[bytes, str], Awaitable[TranscriptResult]]
type StartWorkflow = Callable[[int, str, str], Awaitable[None]]
type SaveAudio = Callable[[bytes, str], str]
type ReadAudio = Callable[[str], bytes]


def save_audio(audio: bytes, mimetype: str) -> str:
    ext = mimetypes.guess_extension(mimetype) or ".m4a"
    UPLOADS_DIR.mkdir(exist_ok=True)
    path = UPLOADS_DIR / f"{uuid.uuid4()}{ext}"
    path.write_bytes(audio)
    return str(path)


async def enqueue(
    audio: bytes,
    mimetype: str,
    *,
    start_workflow: StartWorkflow,
    save_file: SaveAudio | None = None,
    repo: TranscriptionRepo | None = None,
) -> Transcription:
    """Persist the audio and a pending row, then hand off to the worker.

    The audio itself never crosses the workflow boundary — only its path.
    """
    path = (save_file or save_audio)(audio, mimetype)
    row = (repo or TranscriptionRepo()).add_pending(path)
    await start_workflow(row.id, path, mimetype)
    return row


async def process(
    transcription_id: int,
    audio_path: str,
    mimetype: str,
    *,
    transcribe: Transcribe,
    read_file: ReadAudio | None = None,
    repo: TranscriptionRepo | None = None,
) -> Transcription | None:
    """The worker-side body: transcribe the stored file and record the result.

    Failure marking lives in the workflow, not here, so activity retries
    don't prematurely flip the row to failed.
    """
    audio = (read_file or _read_audio)(audio_path)
    result = await transcribe(audio, mimetype)
    return (repo or TranscriptionRepo()).mark_done(
        transcription_id, result.transcript, result.summary, result.duration_seconds
    )


def _read_audio(path: str) -> bytes:
    return Path(path).read_bytes()


def list_all(repo: TranscriptionRepo | None = None) -> list[Transcription]:
    return (repo or TranscriptionRepo()).list()


def get(transcription_id: int, repo: TranscriptionRepo | None = None) -> Transcription | None:
    return (repo or TranscriptionRepo()).get(transcription_id)
