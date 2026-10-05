#!/usr/bin/env python3
"""Migrate photos from Uploadcare to Bunny CDN.

Usage:
  python3 scripts/migrate-to-bunny.py --dry-run      # only build scripts/bunny-manifest.json
  python3 scripts/migrate-to-bunny.py --skip-upload  # manifest + download + resize
  python3 scripts/migrate-to-bunny.py                # ... and upload (needs env vars below)
  python3 scripts/migrate-to-bunny.py --check        # HEAD every CDN url, expect 200
  python3 scripts/migrate-to-bunny.py --rewrite      # replace Uploadcare urls in the site

Upload settings are read from .env (or the environment): BUNNY_STORAGE_ZONE,
BUNNY_STORAGE_HOST (e.g. storage.bunnycdn.com) and BUNNY_STORAGE_KEY (storage zone password).
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "scripts" / "bunny-manifest.json"
WORK = ROOT / "tmp" / "bunny-migration"
UPLOADED_LOG = WORK / "uploaded.txt"

CDN_URL = "https://ootes-band.b-cdn.net"
UPLOADCARE = "https://ucarecdn.com"

UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
SERIES_DIR = ROOT / "_photo_series"
# Order matters: a photo used on several pages is filed under the first one
PAGES = ["index.html", "releases.html", "strategie.html", "bandleden-gezocht.html"]
EXTENSIONS = {"image/jpeg": "jpg", "image/png": "png", "image/gif": "gif", "image/webp": "webp"}


def load_env():
    """Read KEY=value lines from .env without overriding real env vars."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            os.environ.setdefault(key.strip(), value)


def content_type(uuid):
    req = urllib.request.Request(f"{UPLOADCARE}/{uuid}/", method="HEAD")
    with urllib.request.urlopen(req) as res:
        return res.headers["Content-Type"].split(";")[0]


def build_manifest():
    entries = {}

    for series in sorted(SERIES_DIR.glob("*.md")):
        uuids = re.findall(rf'"uuid"\s*:\s*"?({UUID})"?', series.read_text())
        for i, uuid in enumerate(uuids, 1):
            entries.setdefault(uuid, f"fotos/{series.stem}/{i:02d}")

    for page in PAGES:
        uuids = re.findall(rf"ucarecdn\.com/({UUID})", (ROOT / page).read_text())
        new = [u for u in dict.fromkeys(uuids) if u not in entries]
        for i, uuid in enumerate(new, 1):
            entries[uuid] = f"pagina/{Path(page).stem}/{i:02d}"

    manifest = {}
    for uuid, base in entries.items():
        ext = EXTENSIONS[content_type(uuid)]
        if base.startswith("fotos/") and ext != "jpg":
            sys.exit(f"{uuid}: series photo is {ext}, templates assume jpg")
        manifest[uuid] = {"original": f"original/{base}.{ext}", "web": f"web/{base}.jpg"}
        print(f"{uuid} -> {base}.{ext}")

    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"\n{len(manifest)} photos written to {MANIFEST.relative_to(ROOT)}")
    return manifest


def load_manifest():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    return build_manifest()


def download_and_resize(manifest):
    for uuid, paths in manifest.items():
        original = WORK / paths["original"]
        web = WORK / paths["web"]

        if not original.exists():
            print(f"download {paths['original']}")
            original.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(f"{UPLOADCARE}/{uuid}/", original)

        if not web.exists():
            print(f"resize   {paths['web']}")
            web.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                ["magick", str(original), "-auto-orient", "-resize", "1600x1600>",
                 "-strip", "-quality", "82", str(web)],
                check=True,
            )


def upload(manifest):
    load_env()
    names = ["BUNNY_STORAGE_ZONE", "BUNNY_STORAGE_HOST", "BUNNY_STORAGE_KEY"]
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        sys.exit(f"Missing {', '.join(missing)} in .env; use --skip-upload to only download and resize")
    zone, host, key = (os.environ[n] for n in names)

    done = set(UPLOADED_LOG.read_text().split()) if UPLOADED_LOG.exists() else set()
    for paths in manifest.values():
        for path in (paths["original"], paths["web"]):
            if path in done:
                continue
            print(f"upload   {path}")
            req = urllib.request.Request(
                f"https://{host}/{zone}/{path}",
                data=(WORK / path).read_bytes(),
                method="PUT",
                headers={"AccessKey": key, "Content-Type": "application/octet-stream"},
            )
            urllib.request.urlopen(req).close()
            with UPLOADED_LOG.open("a") as log:
                log.write(path + "\n")


def check(manifest):
    failed = 0
    for paths in manifest.values():
        for path in (paths["original"], paths["web"]):
            url = f"{CDN_URL}/{path}"
            try:
                req = urllib.request.Request(url, method="HEAD")
                status = urllib.request.urlopen(req).status
            except urllib.error.HTTPError as e:
                status = e.code
            if status != 200:
                failed += 1
                print(f"{status} {url}")
    total = 2 * len(manifest)
    print(f"{total - failed}/{total} urls OK")
    return failed == 0


def rewrite(manifest):
    # Series front matter: "uuid": "..." -> "file": "fotos/<serie>/NN.jpg"
    for series in SERIES_DIR.glob("*.md"):
        text = series.read_text()
        new = re.sub(
            rf'"uuid"(\s*):(\s*)"?({UUID})"?',
            lambda m: f'"file"{m[1]}:{m[2]}"{manifest[m[3]]["web"].removeprefix("web/")}"',
            text,
        )
        if new != text:
            series.write_text(new)
            print(f"rewrote {series.relative_to(ROOT)}")

    # Pages: src -> web version, href -> original
    for page in PAGES:
        path = ROOT / page
        text = path.read_text()
        new = re.sub(
            rf'(src|href)="https://ucarecdn\.com/({UUID})/[^"]*"',
            lambda m: f'{m[1]}="{{{{ site.cdn_url }}}}/'
            f'{manifest[m[2]]["web" if m[1] == "src" else "original"]}"',
            text,
        )
        if new != text:
            path.write_text(new)
            print(f"rewrote {page}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="only (re)build the manifest")
    parser.add_argument("--skip-upload", action="store_true", help="download and resize, no upload")
    parser.add_argument("--check", action="store_true", help="check all CDN urls return 200")
    parser.add_argument("--rewrite", action="store_true", help="replace Uploadcare urls in the site")
    args = parser.parse_args()

    if args.dry_run:
        build_manifest()
        return

    manifest = load_manifest()

    if args.check:
        sys.exit(0 if check(manifest) else 1)

    if args.rewrite:
        if not check(manifest):
            sys.exit("Not all photos are on the CDN yet; not rewriting")
        rewrite(manifest)
        return

    download_and_resize(manifest)
    if not args.skip_upload:
        upload(manifest)


if __name__ == "__main__":
    main()
