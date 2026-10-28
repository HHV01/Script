"""Local visual control room for the video pipeline."""
import sys
from pathlib import Path

_SOURCE = str(Path(__file__).resolve().parents[1] / 'src')
if _SOURCE not in sys.path:
    sys.path.insert(0, _SOURCE)
