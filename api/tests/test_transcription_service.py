import asyncio

from services.transcription import TranscriptionService, TranscriptResult
from tests.fixtures import FakeRepo, FakeTranscriber


def make_service(transcript: str = "hello world", duration: float | None = 2.5):
    transcriber = FakeTranscriber(TranscriptResult(transcript, duration))
    repo = FakeRepo()
    return TranscriptionService(transcriber=transcriber, repo=repo), transcriber, repo


def test_create_transcribes_and_persists():
    service, transcriber, repo = make_service()

    row = asyncio.run(service.create(b"\x00\x01audio", "audio/m4a"))

    assert transcriber.calls == [(b"\x00\x01audio", "audio/m4a")]
    assert row.transcript == "hello world"
    assert row.duration_seconds == 2.5
    assert repo.rows == [row]


def test_list_returns_newest_first():
    service, _, _ = make_service()
    first = asyncio.run(service.create(b"a", "audio/m4a"))
    second = asyncio.run(service.create(b"b", "audio/m4a"))

    assert [r.id for r in service.list()] == [second.id, first.id]


def test_get_missing_returns_none():
    service, _, _ = make_service()
    assert service.get(999) is None
