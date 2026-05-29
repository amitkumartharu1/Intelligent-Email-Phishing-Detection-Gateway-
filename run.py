"""
run.py – Application entry-point.
  python run.py
"""
import logging
import sys
from pathlib import Path

from app import create_app

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

app = create_app()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", False))
