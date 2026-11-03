"""Upload the PAR files to a Zenodo draft, and optionally publish it.

Uploading only changes the draft. Publishing is a separate flag because it can't be undone:
Zenodo doesn't allow the files of a published version to change.

    uv run --env-file .env par-zenodo-upload --new-version-of RECORD  # drafts a new version
    uv run --env-file .env par-zenodo-upload --deposition ID          # updates that draft
    uv run --env-file .env par-zenodo-upload --deposition ID --publish
"""

import argparse
import datetime
import hashlib
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from par.package import VERSION

API = "https://zenodo.org/api/deposit/depositions"
FILES = [
    Path("data/processed/par-datapackage.zip"),
    Path("data/processed/par-diskette.zip"),
    Path("docs/sources/ADA279069.pdf"),
    Path("docs/sources/ADA294527.pdf"),
]
REPO_URL = "https://github.com/jrnold/PAR"

DESCRIPTION = f"""\
<p>Data from the Personnel Attrition Rates (PAR) data diskettes (DTIC ADM000368, version 2.1, \
1994), compiled by Robert L. Helmbold at the US Army Concepts Analysis Agency: personnel \
strengths, casualties, and related data for historical battles and operations.</p>
<p><b>Files</b></p>
<ul>
<li><code>par-datapackage.zip</code>: tidy CSV tables as a Frictionless data package, with the \
reports and their OCR text.</li>
<li><code>par-diskette.zip</code>: the original diskette files, unchanged, except that \
<code>BODASHIP.WQ!</code> is missing.</li>
<li><code>ADA279069.pdf</code>: the catalog that documents the data (CAA-RP-93-4).</li>
<li><code>ADA294527.pdf</code>: addenda to the annotated bibliography (CAA-RP-95-2).</li>
</ul>
<p>The code, known errors in the data, and validation reports are in \
<a href="{REPO_URL}">{REPO_URL}</a>.</p>
<p><b>Licenses</b></p>
<ul>
<li>Diskette files and reports: public domain, as US government works.</li>
<li>Derived tables: <a href="https://opendatacommons.org/licenses/pddl/1-0/">ODC PDDL 1.0</a>.</li>
</ul>
"""


def metadata(publication_date: datetime.date) -> dict[str, Any]:
    """Return the record's metadata."""
    return {
        "title": "Personnel Attrition Rates in Historical Land Combat Operations: data package",
        "upload_type": "dataset",
        "publication_date": publication_date.isoformat(),
        "version": VERSION,
        "description": DESCRIPTION,
        "access_right": "open",
        "license": "pddl-1.0",
        "creators": [{"name": "Arnold, Jeffrey B."}],
        "contributors": [
            {
                "name": "Helmbold, Robert L.",
                "type": "DataCollector",
                "affiliation": "US Army Concepts Analysis Agency",
            }
        ],
        "keywords": ["military history", "battles", "casualties", "attrition", "Lanchester"],
        "related_identifiers": [
            {"identifier": REPO_URL, "relation": "isSupplementedBy", "scheme": "url"},
        ],
    }


def md5(path: Path, chunk: int = 1 << 20) -> str:
    """Return the file's md5, the checksum Zenodo reports."""
    digest = hashlib.md5()  # noqa: S324
    with path.open("rb") as f:
        while block := f.read(chunk):
            digest.update(block)
    return digest.hexdigest()


def request(
    url: str, token: str, method: str = "GET", payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Send a JSON request and return the JSON response."""
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method=method)  # noqa: S310
    req.add_header("Authorization", f"Bearer {token}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=300) as response:  # noqa: S310
            return json.load(response)
    except urllib.error.HTTPError as error:
        # Zenodo explains validation failures in the response body.
        raise RuntimeError(f"{method} {url}: {error.code} {error.read().decode()}") from error


def upload_file(bucket: str, path: Path, token: str) -> dict[str, Any]:
    """Stream one file to the draft's bucket, replacing any file of that name."""
    with path.open("rb") as f:
        req = urllib.request.Request(f"{bucket}/{path.name}", data=f, method="PUT")  # noqa: S310
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Content-Length", str(path.stat().st_size))
        req.add_header("Content-Type", "application/octet-stream")
        try:
            with urllib.request.urlopen(req, timeout=3600) as response:  # noqa: S310
                return json.load(response)
        except urllib.error.HTTPError as error:
            raise RuntimeError(f"PUT {path.name}: {error.code} {error.read().decode()}") from error


def new_version_draft(record: int, token: str) -> dict[str, Any]:
    """Return a draft of a new version of a published record, which keeps its concept DOI."""
    done = request(f"{API}/{record}/actions/newversion", token, method="POST")
    return request(done["links"]["latest_draft"], token)


def check_checksum(path: Path, reported: str) -> None:
    """Fail unless Zenodo's checksum, such as `md5:abc`, matches the local file."""
    expected = md5(path)
    if reported.removeprefix("md5:") != expected:
        raise RuntimeError(f"{path.name}: Zenodo reports {reported}, local md5 is {expected}")


def main() -> None:
    """Draft a new version, update a draft, or publish one when asked."""
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--deposition", type=int, help="id of an existing Zenodo draft")
    target.add_argument(
        "--new-version-of", type=int, metavar="RECORD", help="published record to add a version to"
    )
    parser.add_argument("--publish", action="store_true", help="publish the draft as it stands")
    args = parser.parse_args()
    if args.publish and args.deposition is None:
        parser.error("--publish needs --deposition")
    token = os.environ["ZENODO_API_KEY"]

    if args.publish:
        done = request(f"{API}/{args.deposition}/actions/publish", token, method="POST")
        print(f"published {done['doi']}: {done['links']['record_html']}")
        return

    missing = [str(path) for path in FILES if not path.exists()]
    if missing:
        raise FileNotFoundError(f"run dvc repro first; missing {missing}")
    if args.new_version_of is not None:
        draft = new_version_draft(args.new_version_of, token)
    else:
        draft = request(f"{API}/{args.deposition}", token)
    url = f"{API}/{draft['id']}"
    # Send the metadata first, so a rejection doesn't come after the uploads.
    request(
        url,
        token,
        method="PUT",
        payload={"metadata": metadata(datetime.datetime.now(datetime.UTC).date())},
    )
    existing = {f["filename"]: f["checksum"].removeprefix("md5:") for f in draft.get("files", [])}
    for path in FILES:
        if existing.get(path.name) == md5(path):
            print(f"already on the draft: {path}", flush=True)
            continue
        print(f"uploading {path} ({path.stat().st_size} bytes)", flush=True)
        check_checksum(path, upload_file(draft["links"]["bucket"], path, token)["checksum"])
    print(f"draft {draft['id']} updated, not published: {draft['links']['html']}")


if __name__ == "__main__":
    main()
