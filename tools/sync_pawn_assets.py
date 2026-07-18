"""Copy all piece sprites from assets.zip in Downloads."""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ZIP = Path.home() / "Downloads" / "assets.zip"
DEST = ROOT / "assets" / "pieces_mine"
ZIP_PREFIX = "assets/pieces_mine/"


def sync_pieces(
    zip_path: Path = DEFAULT_ZIP,
    dest_root: Path = DEST,
) -> None:
    if not zip_path.exists():
        raise FileNotFoundError(f"Missing zip file: {zip_path}")

    if dest_root.exists():
        shutil.rmtree(dest_root)
    dest_root.mkdir(parents=True)

    with zipfile.ZipFile(zip_path) as archive:
        members = [
            name for name in archive.namelist()
            if name.startswith(ZIP_PREFIX) and not name.endswith("/")
        ]
        if not members:
            raise FileNotFoundError(f"No pieces_mine files in {zip_path}")

        for member in members:
            relative = Path(member).relative_to(ZIP_PREFIX)
            out_path = dest_root / relative
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as src, open(out_path, "wb") as dst:
                dst.write(src.read())

    piece_folders = sorted(p.name for p in dest_root.iterdir() if p.is_dir())
    total = len(list(dest_root.rglob("*.png")))
    print(f"Synced pieces -> {dest_root}")
    print(f"  folders: {', '.join(piece_folders)}")
    print(f"  total: {total} png files")


def main():
    sync_pieces()


if __name__ == "__main__":
    main()
