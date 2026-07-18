"""Copy pieces1 assets from CTD26 into the project."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CTD26_PIECES1 = ROOT.parent / "CTD26" / "pieces1"
ASSETS_PIECES1 = ROOT / "assets" / "pieces1"


def copy_pieces1(
    src_root: Path = CTD26_PIECES1,
    dst_root: Path = ASSETS_PIECES1,
) -> None:
    if not src_root.exists():
        raise FileNotFoundError(f"Missing source folder: {src_root}")

    if dst_root.exists():
        shutil.rmtree(dst_root)
    shutil.copytree(src_root, dst_root)

    total = len(list(dst_root.rglob("*.png")))
    print(f"Copied pieces1 -> {dst_root} ({total} sprites)")


def main():
    copy_pieces1()


if __name__ == "__main__":
    main()
