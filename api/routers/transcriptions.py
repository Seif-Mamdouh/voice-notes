from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

from clients.deepgram import transcribe
from models import Transcription
from services.transcription import create, get, list_all

router = APIRouter(prefix="/transcriptions", tags=["transcriptions"])


class TranscriptionResponse(BaseModel):
    id: int
    transcript: str
    duration_seconds: float | None
    created_at: str  # ISO 8601 — JSON-safe boundary


class TranscriptionListResponse(BaseModel):
    transcriptions: list[TranscriptionResponse]


def to_response(row: Transcription) -> TranscriptionResponse:
    return TranscriptionResponse(
        id=row.id,
        transcript=row.transcript,
        duration_seconds=row.duration_seconds,
        created_at=row.created_at.isoformat(),
    )


@router.post("", response_model=TranscriptionResponse)
async def create_transcription(file: UploadFile) -> TranscriptionResponse:
    audio = await file.read()
    if not audio:
        raise HTTPException(status_code=400, detail="Empty audio file")
    row = await create(audio, file.content_type or "audio/m4a", transcribe=transcribe)
    return to_response(row)


@router.get("", response_model=TranscriptionListResponse)
def list_transcriptions() -> TranscriptionListResponse:
    return TranscriptionListResponse(transcriptions=[to_response(r) for r in list_all()])


@router.get("/{transcription_id}", response_model=TranscriptionResponse)
def get_transcription(transcription_id: int) -> TranscriptionResponse:
    row = get(transcription_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Transcription not found")
    return to_response(row)
