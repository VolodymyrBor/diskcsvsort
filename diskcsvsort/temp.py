import os
import tempfile
import platform
from pathlib import Path
from typing import ContextManager
from contextlib import contextmanager

from diskcsvsort.enums import OS


@contextmanager
def get_path_tempfile(
    directory: Path | None = None,
    delete: bool = True,
    suffix: str = '',
) -> ContextManager[Path]:

    temp_dir = directory if directory else Path(tempfile.gettempdir())
    temp_dir.mkdir(parents=True, exist_ok=True)

    if platform.system() == OS.WINDOWS:
        filename = os.urandom(24).hex()
        filepath = temp_dir / f'{filename}{suffix}'
        filepath.touch(exist_ok=True)
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=temp_dir) as file:
            filepath = Path(file.name)

    try:
        yield filepath
    finally:
        if delete:
            filepath.unlink(missing_ok=True)
