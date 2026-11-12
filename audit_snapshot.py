#!/usr/bin/env python3
"""Audit a quiz ZIP file for architecture risks without printing private values."""
import sys
import zipfile
from pathlib import PurePosixPath


def main(path: str) -> None:
    with zipfile.ZipFile(path) as z:
        names = [i.filename for i in z.infolist() if not i.is_dir()]
        risks = []
        for name in names:
            low = name.lower()
            if name.startswith("/") or ".." in PurePosixPath(name).parts or "\\" in name:
                risks.append("UNSAFE PATH: " + name)
            if any(fragment in low for fragment in ("private/config.php", ".jsonl", ".log", ".bak.", ".env", "lead-backup.php")):
                risks.append("SENSITIVE/INTERNAL FILE PRESENT: " + name)
            if name.endswith("setup.php") or name.endswith("setup.php.disabled"):
                risks.append("INSTALLER FILE PRESENT: " + name)
        print("Files:", len(names), "Total bytes:", sum(i.file_size for i in z.infolist()))
        print("Risk items:", len(risks))
        for item in risks:
            print(item)
        print("Archive CRC:", "OK" if z.testzip() is None else "BAD")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: audit_snapshot.py site.zip")
    main(sys.argv[1])
