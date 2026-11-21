"""Private file creation shared by diagnostic stores; no server imports."""

import os
from pathlib import Path


def private_open(path: Path, mode: str, **kwargs):
    """Create private from the first byte, also repair a leftover/replaced existing file."""
    if path.exists():
        path.chmod(0o600)

    def opener(name, flags):
        descriptor = os.open(name, flags, 0o600)
        try:
            os.chmod(name, 0o600)  # exact even under an unusually restrictive umask
        except Exception:
            os.close(descriptor)
            raise
        return descriptor

    return open(path, mode, opener=opener, **kwargs)


