from pathlib import Path
import os

# def get_output_dir(subdir: str | None = None) -> Path:
#     base = Path(os.environ.get("OUTPUT_DIR", "plots"))
#     path = base / subdir if subdir else base
#     path.mkdir(parents=True, exist_ok=True)
#     return path

def get_output_dir(subdir: str | None = None) -> Path:
    # Project root = parent of src/
    project_root = Path(__file__).resolve().parent.parent.parent

    base = Path(os.environ.get("OUTPUT_DIR", project_root / "plots"))
    path = base / subdir if subdir else base
    path.mkdir(parents=True, exist_ok=True)
    return path