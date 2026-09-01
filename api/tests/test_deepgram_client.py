"""Parsing tests against a canned Deepgram prerecorded-API payload."""

from clients.deepgram import parse_deepgram_response

DEEPGRAM_PAYLOAD = {
    "metadata": {"duration": 3.84, "channels": 1, "models": ["nova-3"]},
    "results": {
        "channels": [
            {
                "alternatives": [
                    {
                        "transcript": "Testing one two three.",
                        "confidence": 0.998,
                        "words": [],
                    }
                ]
            }
        ]
    },
}


def test_parses_transcript_and_duration():
    result = parse_deepgram_response(DEEPGRAM_PAYLOAD)
    assert result.transcript == "Testing one two three."
    assert result.duration_seconds == 3.84


def test_empty_alternatives_yields_empty_transcript():
    payload = {"metadata": {}, "results": {"channels": [{"alternatives": []}]}}
    result = parse_deepgram_response(payload)
    assert result.transcript == ""
    assert result.duration_seconds is None
