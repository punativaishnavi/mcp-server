"""Sandboxed filesystem tools.

Every path is resolved inside WORKSPACE_DIR; anything escaping it
(e.g. via '..') raises ValueError before any I/O happens.
"""

import os
import re

WORKSPACE_DIR = os.path.abspath(os.environ.get("MCP_WORKSPACE", "workspace"))


def _resolve(path: str) -> str:
    candidate = os.path.abspath(os.path.join(WORKSPACE_DIR, path))
    if candidate != WORKSPACE_DIR and not candidate.startswith(WORKSPACE_DIR + os.sep):
        raise ValueError(f"Path escapes workspace: {path!r}")
    return candidate


def list_dir(path: str = ".") -> list[str]:
    """List files and directories in the sandboxed workspace."""
    target = _resolve(path)
    if not os.path.isdir(target):
        raise ValueError(f"Not a directory: {path!r}")
    return sorted(os.listdir(target))


def read_file(path: str) -> str:
    """Read a text file from the sandboxed workspace."""
    target = _resolve(path)
    if not os.path.isfile(target):
        raise ValueError(f"File not found: {path!r}")
    with open(target, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def write_file(path: str, content: str) -> str:
    """Write (or overwrite) a text file in the sandboxed workspace."""
    target = _resolve(path)
    os.makedirs(os.path.dirname(target) or WORKSPACE_DIR, exist_ok=True)
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(content)
    return f"Wrote {len(content)} characters to {path}"


def search_files(pattern: str, path: str = ".") -> list[dict]:
    """Grep for a regex pattern across text files in the workspace.

    Returns [{file, line_no, line}] matches, capped at 50.
    """
    rx = re.compile(pattern)
    hits: list[dict] = []
    root = _resolve(path)
    for dirpath, _, filenames in os.walk(root):
        for fname in sorted(filenames):
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="strict") as fh:
                    for i, line in enumerate(fh, 1):
                        if rx.search(line):
                            hits.append({"file": os.path.relpath(fpath, WORKSPACE_DIR),
                                         "line_no": i, "line": line.rstrip()})
                            if len(hits) >= 50:
                                return hits
            except (UnicodeDecodeError, OSError):
                continue  # skip binary / unreadable files
    return hits
