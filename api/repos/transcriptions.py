from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from db import session_factory
from models import Transcription, TranscriptionStatus


class TranscriptionRepo:
    """Data access for transcriptions. The only layer that touches the DB."""

    def __init__(self, sessions: Callable[[], Session] = session_factory):
        self._sessions = sessions

    def add_pending(self, audio_path: str) -> Transcription:
        with self._sessions() as session:
            row = Transcription(status=TranscriptionStatus.PENDING, audio_path=audio_path)
            session.add(row)
            session.commit()
            return row

    def mark_done(
        self,
        transcription_id: int,
        transcript: str,
        summary: str | None,
        duration_seconds: float | None,
    ) -> Transcription | None:
        with self._sessions() as session:
            row = session.get(Transcription, transcription_id)
            if row is None:
                return None
            row.status = TranscriptionStatus.DONE
            row.transcript = transcript
            row.summary = summary
            row.duration_seconds = duration_seconds
            session.commit()
            return row

    def mark_failed(self, transcription_id: int) -> Transcription | None:
        with self._sessions() as session:
            row = session.get(Transcription, transcription_id)
            if row is None:
                return None
            row.status = TranscriptionStatus.FAILED
            session.commit()
            return row

    def list(self) -> list[Transcription]:
        with self._sessions() as session:
            stmt = select(Transcription).order_by(Transcription.created_at.desc())
            return list(session.scalars(stmt))

    def get(self, transcription_id: int) -> Transcription | None:
        with self._sessions() as session:
            return session.get(Transcription, transcription_id)
