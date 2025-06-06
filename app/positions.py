import json
from pathlib import Path

POSITIONS_FILE = Path("app/positions.json")

def load_positions() -> dict:
    if POSITIONS_FILE.exists():
        with open(POSITIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_positions(positions: dict):
    with open(POSITIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(positions, f, ensure_ascii=False, indent=2)
