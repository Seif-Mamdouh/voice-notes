import os

import httpx
from fastapi import HTTPException

from services.transcription import TranscriptResult

DEEPGRAM_URL = "https://api.deepgram.com/v1/listen"
DEEPGRAM_PARAMS = {"model": "nova-3", "smart_format": "true"}


def _api_key(explicit: str | None = None) -> str:
    key = explicit or os.environ.get("DEEPGRAM_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="DEEPGRAM_API_KEY is not configured")
    return key


async def transcribe(audio: bytes, mimetype: str, api_key: str | None = None) -> TranscriptResult:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            DEEPGRAM_URL,
            params=DEEPGRAM_PARAMS,
            headers={"Authorization": f"Token {_api_key(api_key)}", "Content-Type": mimetype},
            content=audio,
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Deepgram error {response.status_code}: {response.text[:200]}",
        )
    return parse_deepgram_response(response.json())


def parse_deepgram_response(payload: dict) -> TranscriptResult:
    alternatives = payload["results"]["channels"][0]["alternatives"]
    transcript = alternatives[0]["transcript"] if alternatives else ""
    duration = payload.get("metadata", {}).get("duration")
    return TranscriptResult(transcript=transcript, duration_seconds=duration)
