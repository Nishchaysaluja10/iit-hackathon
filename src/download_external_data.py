# download_external_data.py
"""Utility to download all files from a public Google‑Drive folder.

The script uses the `gdown` package to download the entire folder contents.
It does not attempt to list files individually – `gdown` handles the folder
download when the `--folder` flag is provided.

Usage example::
    python -m src.download_external_data \
        --folder-id 1Z1Pt3XoF7GAb_QtLksa8q4D_U-wc65e4 \
        --dest data/external
"""
import argparse
import subprocess
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Download all files from a public Google‑Drive folder.")
    parser.add_argument("--folder-id", required=True, help="Google‑Drive folder ID (the part after /folders/)")
    parser.add_argument("--dest", default="data/external", help="Destination directory for downloaded files")
    args = parser.parse_args()

    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    folder_url = f"https://drive.google.com/drive/folders/{args.folder_id}"
    print(f"Downloading folder {folder_url} into {dest}")
    try:
        import sys
        subprocess.run([sys.executable, "-m", "gdown", folder_url, "--folder"], cwd=str(dest), check=True)
    except subprocess.CalledProcessError as e:
        print("Failed to download folder:", e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
