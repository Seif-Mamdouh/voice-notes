import os

import httpx

from services.transcription import TranscriptResult

DEEPGRAM_URL = "https://api.deepgram.com/v1/listen"
DEEPGRAM_PARAMS = {"model": "nova-3", "smart_format": "true", "summarize": "v2"}


class DeepgramError(Exception):
    """Deepgram returned a non-200 response."""


class DeepgramConfigError(Exception):
    """DEEPGRAM_API_KEY is not configured. Non-retryable."""


def _api_key(explicit: str | None = None) -> str:
    key = explicit or os.environ.get("DEEPGRAM_API_KEY")
    if not key:
        raise DeepgramConfigError("DEEPGRAM_API_KEY is not configured")
    return key


async def transcribe(audio: bytes, mimetype: str, api_key: str | None = None) -> TranscriptResult:
    # Long recordings can take minutes to process; only the connect is kept tight.
    async with httpx.AsyncClient(timeout=httpx.Timeout(600, connect=10)) as client:
        response = await client.post(
            DEEPGRAM_URL,
            params=DEEPGRAM_PARAMS,
            headers={"Authorization": f"Token {_api_key(api_key)}", "Content-Type": mimetype},
            content=audio,
        )
    if response.status_code != 200:
        raise DeepgramError(f"Deepgram error {response.status_code}: {response.text[:200]}")
    return parse_deepgram_response(response.json())


def parse_deepgram_response(payload: dict) -> TranscriptResult:
    alternatives = payload["results"]["channels"][0]["alternatives"]
    transcript = alternatives[0]["transcript"] if alternatives else ""
    duration = payload.get("metadata", {}).get("duration")
    # summarize=v2 is English-only and can be absent — a missing summary is not an error.
    summary = payload["results"].get("summary", {}).get("short") or None
    return TranscriptResult(transcript=transcript, duration_seconds=duration, summary=summary)
