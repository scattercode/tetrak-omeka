#!/usr/bin/env python3
"""Transcribe pages in Omeka with Tetrak, and write the transcripts back.

For each page (each media) that has no transcript yet, this downloads the
image from Omeka, runs the Tetrak CLI on it, and saves the result to the page
as its "Tetrak transcript" (tetrak:transcript), with "Transcribed with"
recording the Tetrak release, backend and date. The sites' reader shows both
beside the image. tutorials/transcribe-with-tetrak.md walks through it.

Which pages: by default, every page with neither a Tetrak transcript nor a
reference transcript, so the pages that already show a verified transcript
are left alone. --include-reference transcribes those too, to compare
Tetrak's reading with the reference; --redo replaces earlier Tetrak
transcripts.

Which backend: easyocr-hy, Tetrak's Armenian recogniser, for items whose
dcterms:language is "hy"; auto-local, which runs every local engine and keeps
the best, for the rest. --backend names one backend for every page.

Prerequisites: Python 3.11 or later; a seeded Omeka and its API key in
.omeka-api.env (scripts/reset.sh); and Tetrak installed, so that tetrak-ocr
is on the PATH (or named with --tetrak-ocr). For the default backends:

    pip install 'tetrak[armenian,qa,vision]==5.14.1'

Before transcribing anything it checks, with `tetrak-ocr backends`, that the
backends it is about to use are installed, and says which tetrak-ocr it is
running: a different one earlier on the PATH is the usual cause of a backend
that "is not installed" after installing it.

Usage:
    python3 scripts/transcribe.py                                  # every untranscribed page
    python3 scripts/transcribe.py --item tumanyan-death-of-kikos   # one item
    python3 scripts/transcribe.py --collection los-angeles-ephemera
    python3 scripts/transcribe.py --dry-run                        # list, change nothing
    python3 scripts/transcribe.py --item kar-mi-troupe-poster --include-reference
"""

from __future__ import annotations

import argparse
import datetime
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from seed import Omeka, OmekaError, credentials

INSTALL = "pip install 'tetrak[armenian,qa,vision]==5.14.1'"
ARMENIAN_BACKEND = "easyocr-hy"
DEFAULT_BACKEND = "auto-local"
# Tetrak's batch mode sends a transcript scoring below this to triage rather
# than treating it as read. `tetrak-ocr ocr` has no triage, so the score is
# carried into "Transcribed with" and a page under it is called out.
QUALITY_FLOOR = 0.10


def first_value(resource: dict, term: str) -> str | None:
    values = resource.get(term) or []
    return values[0].get("@value") if values else None


def tetrak_version(tetrak_ocr: str) -> str:
    """The installed Tetrak release. The CLI has no --version, so ask the
    Python environment it was installed into."""
    python = Path(tetrak_ocr).resolve().parent / "python"
    try:
        out = subprocess.run(
            [str(python), "-c", "import importlib.metadata as m; print(m.version('tetrak'))"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown version"


def available_backends(tetrak_ocr: str) -> set[str]:
    """The backends this tetrak-ocr can run: the ticked lines of
    `tetrak-ocr backends`, e.g. " ✓ easyocr-hy"."""
    out = subprocess.run([tetrak_ocr, "backends"], capture_output=True, text=True)
    return {
        line.split()[1]
        for line in out.stdout.splitlines()
        if line.strip().startswith("✓")
    }


def select_items(omeka: Omeka, args) -> list[dict]:
    if args.item:
        item = omeka.find_by_identifier("items", args.item)
        if not item:
            raise OmekaError(f"no item with the identifier {args.item}")
        return [item]
    query = {"per_page": 1000}
    if args.collection:
        item_set = omeka.find_by_identifier("item_sets", args.collection)
        if not item_set:
            raise OmekaError(f"no collection with the identifier {args.collection}")
        query["item_set_id"] = item_set["o:id"]
    return omeka.get("items", **query)


def transcribe(image: Path, backend: str, tetrak_ocr: str) -> tuple[str, str, float | None]:
    """Run `tetrak-ocr ocr` on one image. Returns the transcript, the engine
    that produced it, and its quality score; auto-local reports the last two
    on stderr, and other backends do not score."""
    output = image.with_suffix(".txt")
    result = subprocess.run(
        [tetrak_ocr, "ocr", str(image), "--backend", backend, "--output", str(output)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        detail = "\n".join(result.stderr.strip().splitlines()[-5:])
        raise RuntimeError(f"tetrak-ocr failed:\n{detail}")
    engine, quality = backend, None
    for line in result.stderr.splitlines():
        # auto-local's verdict: "[auto-local → vision]  effective=0.21  quality=0.24"
        if line.strip().startswith("[auto-local →"):
            engine = "auto-local → " + line.split("→", 1)[1].split("]", 1)[0].strip()
            for field in line.split():
                if field.startswith("quality="):
                    quality = float(field.removeprefix("quality="))
    return output.read_text(encoding="utf-8").strip(), engine, quality


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    which = parser.add_mutually_exclusive_group()
    which.add_argument("--item", metavar="IDENTIFIER", help="only this item")
    which.add_argument("--collection", metavar="IDENTIFIER", help="only this collection's items")
    parser.add_argument("--backend", help="use this Tetrak backend for every page")
    parser.add_argument("--include-reference", action="store_true",
                        help="also transcribe pages that have a reference transcript")
    parser.add_argument("--redo", action="store_true",
                        help="replace Tetrak transcripts written by an earlier run")
    parser.add_argument("--dry-run", action="store_true",
                        help="list the pages that would be transcribed, and stop")
    parser.add_argument("--tetrak-ocr", default="tetrak-ocr", metavar="PATH",
                        help="the Tetrak CLI to run (default: tetrak-ocr on the PATH)")
    args = parser.parse_args()

    tetrak_ocr = shutil.which(args.tetrak_ocr)
    if not tetrak_ocr and not args.dry_run:
        sys.exit("transcribe.py: tetrak-ocr not found -- install Tetrak and activate "
                 "its virtual environment (see tutorials/transcribe-with-tetrak.md)")

    omeka = Omeka(*credentials())
    try:
        transcript_id = omeka.term_id("properties", "tetrak:transcript")
        with_id = omeka.term_id("properties", "tetrak:transcribedWith")

        work = []
        for item in select_items(omeka, args):
            language = first_value(item, "dcterms:language")
            backend = args.backend or (ARMENIAN_BACKEND if language == "hy" else DEFAULT_BACKEND)
            for media in omeka.get("media", item_id=item["o:id"], per_page=1000):
                if media.get("tetrak:transcript") and not args.redo:
                    continue
                if media.get("tetrak:referenceTranscript") and not args.include_reference:
                    continue
                work.append((item, media, backend, language))
    except OmekaError as error:
        sys.exit(f"transcribe.py: {error}")

    if not work:
        print("Nothing to transcribe: every selected page has a transcript.")
        return 0
    if args.dry_run:
        for item, media, backend, _ in work:
            print(f"{item['o:title']} / {media['o:title']} ({media['o:source']}): {backend}")
        print(f"{len(work)} page(s) would be transcribed.")
        return 0

    version = tetrak_version(tetrak_ocr)
    print(f"Using {tetrak_ocr} (Tetrak {version})")
    missing = sorted({backend for _, _, backend, _ in work} - available_backends(tetrak_ocr))
    if missing:
        sys.exit(
            f"transcribe.py: this tetrak-ocr cannot run {', '.join(missing)}.\n"
            f"Install the extras into the environment it belongs to:\n    {INSTALL}\n"
            "and check that `which tetrak-ocr` points into that environment."
        )
    today = datetime.date.today().isoformat()
    failures = 0
    with tempfile.TemporaryDirectory(prefix="tetrak-omeka-") as tmp:
        for item, media, backend, language in work:
            label = f"{item['o:title']} / {media['o:title']}"
            print(f"{label}: {backend} ...", end="", flush=True)
            try:
                # The original file, as uploaded, under its own name so that
                # Tetrak sees the right extension.
                image = Path(tmp) / f"{media['o:id']}-{Path(media['o:source']).name}"
                urllib.request.urlretrieve(media["o:original_url"], image)
                text, engine, quality = transcribe(image, backend, tetrak_ocr)
            except (OSError, RuntimeError) as error:
                failures += 1
                print(f" failed\n  {error}")
                continue

            # Omeka replaces every value when a request carries any, so fetch
            # the page's full record, change the two properties, and send the
            # whole record back.
            record = omeka.get(f"media/{media['o:id']}")
            value = {"type": "literal", "property_id": transcript_id, "@value": text}
            if language:
                value["@language"] = language
            record["tetrak:transcript"] = [value]
            scored = f", quality {quality:.2f}" if quality is not None else ""
            record["tetrak:transcribedWith"] = [{
                "type": "literal", "property_id": with_id,
                "@value": f"Tetrak {version}, {engine}{scored}, {today}",
            }]
            try:
                omeka.put(f"media/{media['o:id']}", record)
            except OmekaError as error:
                failures += 1
                print(f" failed\n  {error}")
                continue
            print(f" {len(text)} characters, via {engine}{scored}")
            if quality is not None and quality < QUALITY_FLOOR:
                print(f"  below Tetrak's quality floor of {QUALITY_FLOOR}: "
                      "a batch run would have sent it to triage")

    print(f"Done: {len(work) - failures} page(s) transcribed, {failures} failed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
