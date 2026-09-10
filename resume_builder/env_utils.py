import os
from pathlib import Path


def load_environment(base_dir=None):
    base_path = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
    env_file = base_path / '.env'

    if not env_file.exists():
        return

    for line in env_file.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue

        key, value = [part.strip() for part in line.split('=', 1)]
        if key and value and key not in os.environ:
            os.environ[key] = value
