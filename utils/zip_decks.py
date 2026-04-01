import re
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path

def addToZip(zf, path, zippath):
    if path.is_file():
        zf.write(path, zippath, ZIP_DEFLATED)
    elif path.is_dir():
        if zippath:
            zf.write(path, zippath)
        for nm in sorted(path.iterdir()):
            addToZip(zf,
                     nm, zippath / nm.name)

def get_zip_filename(deck_dir, version):
    # deck_dir is expected to be 'AGAP' or 'AGAP_TTS'
    return f"{deck_dir}_{version}.zip"

def zip_decks(version=None):
    root = Path.cwd()
    build_dir = root / "build"
    desc_file = root / "src" / "headers" / "desc.html"

    if version is None:
        if desc_file.exists():
            content = desc_file.read_text()
            m = re.search(r"AGAP (v[0-9]+\.[0-9]+)", content)
            if m:
                version = m.group(1)
            else:
                version = "v1.0" # Fallback
        else:
            version = "v1.0"

    if build_dir.is_dir():
        for deck_dir in build_dir.iterdir():
            if deck_dir.is_dir() and deck_dir.name in ["AGAP", "AGAP_TTS"]:
                deck_dir_name = deck_dir.name
                zip_name = build_dir / get_zip_filename(deck_dir_name, version)
                print(f"Creating {zip_name}...")
                with ZipFile(zip_name, "w") as zf:
                    addToZip(zf, deck_dir, Path(deck_dir_name))

if __name__ == "__main__":
    zip_decks()
