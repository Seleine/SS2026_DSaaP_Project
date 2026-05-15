from pathlib import Path
import os


def get_output_dir(subdir: str | None = None) -> Path:
    """
    Return the directory used for storing generated output files (e.g. plots).

    The base output directory is determined as follows:
    - If the environment variable ``OUTPUT_DIR`` is set (e.g. when running
      inside a Docker container), it is used as the base output directory.
    - Otherwise, a ``plots`` directory in the project root is used.

    The output directory (and optional subdirectory) is created if it does
    not already exist.

    Notes
    -----
    When using Docker with volume mounts (e.g. via Docker Compose), the
    corresponding host directory must exist prior to starting the container.

    Parameters
    ----------
    subdir : str or None, optional
        Optional subdirectory within the output directory
        (e.g. ``"quality_control"``). If None, the base output directory
        is returned.

    Returns
    -------
    pathlib.Path
        Path to the output directory (or subdirectory). The directory
        is guaranteed to exist.

    """
    project_root = Path(__file__).resolve().parent.parent.parent

    base = Path(os.environ.get("OUTPUT_DIR", project_root / "plots"))
    path = base / subdir if subdir else base
    path.mkdir(parents=True, exist_ok=True)

    return path
