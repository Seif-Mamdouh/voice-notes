"""Print the FastAPI app's OpenAPI spec to stdout — no server needed.

Used by app-mobile's `npm run generate:api` and the CI drift check.
"""

import json
import os
import sys
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite://"  # in-memory; avoid touching the dev DB on import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import app  # noqa: E402

print(json.dumps(app.openapi(), indent=2, sort_keys=True))
