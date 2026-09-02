from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy.orm import Mapped, mapped_column

from db import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class TranscriptionStatus(StrEnum):
    PENDING = "pending"
    DONE = "done"
    FAILED = "failed"


class Transcription(Base):
    __tablename__ = "transcriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(default=TranscriptionStatus.PENDING)
    transcript: Mapped[str | None] = mapped_column(default=None)
    summary: Mapped[str | None] = mapped_column(default=None)
    audio_path: Mapped[str | None] = mapped_column(default=None)
    duration_seconds: Mapped[float | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
