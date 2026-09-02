import asyncio

from services.transcription import TranscriptResult, create, get, list_all
from tests.fixtures import FakeRepo, fake_transcribe


def test_create_transcribes_and_persists():
    transcribe, calls = fake_transcribe(TranscriptResult("hello world", 2.5))
    repo = FakeRepo()

    row = asyncio.run(create(b"\x00\x01audio", "audio/m4a", transcribe=transcribe, repo=repo))

    assert calls == [(b"\x00\x01audio", "audio/m4a")]
    assert row.transcript == "hello world"
    assert row.duration_seconds == 2.5
    assert repo.rows == [row]


def test_list_returns_newest_first():
    transcribe, _ = fake_transcribe(TranscriptResult("hello world", 2.5))
    repo = FakeRepo()
    first = asyncio.run(create(b"a", "audio/m4a", transcribe=transcribe, repo=repo))
    second = asyncio.run(create(b"b", "audio/m4a", transcribe=transcribe, repo=repo))

    assert [r.id for r in list_all(repo=repo)] == [second.id, first.id]


def test_get_missing_returns_none():
    repo = FakeRepo()
    assert get(999, repo=repo) is None
