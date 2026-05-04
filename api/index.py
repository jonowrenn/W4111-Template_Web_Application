import sys
from pathlib import Path

# Ensure project root is on the path when running inside Vercel's /api sandbox
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app  # noqa: F401  — Vercel looks for `app`
