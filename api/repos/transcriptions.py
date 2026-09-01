from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from db import session_factory
from models import Transcription


class TranscriptionRepo:
    """Data access for transcriptions. The only layer that touches the DB."""

    def __init__(self, sessions: Callable[[], Session] = session_factory):
        self._sessions = sessions

    def add(self, transcript: str, duration_seconds: float | None) -> Transcription:
        with self._sessions() as session:
            row = Transcription(transcript=transcript, duration_seconds=duration_seconds)
            session.add(row)
            session.commit()
            return row

    def list(self) -> list[Transcription]:
        with self._sessions() as session:
            stmt = select(Transcription).order_by(Transcription.created_at.desc())
            return list(session.scalars(stmt))

    def get(self, transcription_id: int) -> Transcription | None:
        with self._sessions() as session:
            return session.get(Transcription, transcription_id)
