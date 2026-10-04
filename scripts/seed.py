#!/usr/bin/env python3
"""Load the collections under collections/ into Omeka through its REST API.

Each collections/<name>/collection.toml describes one Omeka item set, its
items, each item's media files, and optionally a site to show them;
collections/vocabularies.toml adds the vocabulary terms they use beyond
Omeka's own. collections/README.md has the format. Everything goes through
the public API, the same one the tutorials use.

Safe to re-run. Vocabularies are matched on prefix, sites on slug, item sets
and items on dcterms:identifier, and a media file on its file name within the
item, so only what is missing is created. Records that already exist are left as they are, except that an
item is added to its collection's site if it is missing from it: to apply
edited metadata, reset the instance (scripts/reset.sh). An interrupted run picks up
where it stopped.

Prerequisites: Python 3.11 or later, standard library only; a running,
installed Omeka; and its API key, which scripts/install.sh writes to
.omeka-api.env, or to .omeka-api.<project>.env for an instance run under
another COMPOSE_PROJECT_NAME. The project is worked out as Compose does, so
the key read is always the instance's own. OMEKA_URL, OMEKA_KEY_IDENTITY and
OMEKA_KEY_CREDENTIAL in the environment take precedence over the file.

Usage:
    python3 scripts/seed.py                        # every collection
    python3 scripts/seed.py los-angeles-ephemera    # just these
"""

from __future__ import annotations

import json
import mimetypes
import os
import re
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COLLECTIONS = ROOT / "collections"


def compose_project() -> tuple[str, str]:
    """The Compose project these scripts are pointed at, and the default.

    The same precedence as Compose: COMPOSE_PROJECT_NAME in the environment,
    then in .env, then compose.yaml's own name.
    """
    default = re.search(r"^name:\s*(\S+)", (ROOT / "compose.yaml").read_text(), re.M).group(1)
    if os.environ.get("COMPOSE_PROJECT_NAME"):
        return os.environ["COMPOSE_PROJECT_NAME"], default
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            key, sep, value = line.partition("=")
            if sep and key.strip() == "COMPOSE_PROJECT_NAME" and value.strip():
                return value.strip(), default
    return default, default


def key_file() -> Path:
    """Where scripts/install.sh wrote this instance's API key.

    One file per Compose project, so installing a second copy alongside
    never redirects the scripts away from the first.
    """
    project, default = compose_project()
    return ROOT / (".omeka-api.env" if project == default else f".omeka-api.{project}.env")


class OmekaError(Exception):
    pass


class Omeka:
    """The handful of Omeka S API calls seeding needs."""

    def __init__(self, url: str, identity: str, credential: str):
        self.api = url.rstrip("/") + "/api"
        self.auth = {"key_identity": identity, "key_credential": credential}
        self._terms: dict[tuple[str, str], int] = {}

    def request(self, method, path, query=None, body=None, content_type=None):
        params = urllib.parse.urlencode({**(query or {}), **self.auth}, doseq=True)
        request = urllib.request.Request(
            f"{self.api}/{path}?{params}", data=body, method=method
        )
        if content_type:
            request.add_header("Content-Type", content_type)
        try:
            with urllib.request.urlopen(request) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")
            try:
                detail = json.dumps(json.loads(detail)["errors"], ensure_ascii=False)
            except (ValueError, KeyError, TypeError):
                detail = detail[:500]
            raise OmekaError(f"{method} {path}: HTTP {error.code}: {detail}") from None
        except urllib.error.URLError as error:
            raise OmekaError(f"cannot reach {self.api}: {error.reason}") from None

    def get(self, path, **query):
        return self.request("GET", path, query)

    def post(self, path, data):
        body = json.dumps(data).encode()
        return self.request("POST", path, body=body, content_type="application/json")

    def patch(self, path, data):
        """Update only the fields given; Omeka leaves the rest as they are.

        Except metadata: a PATCH carrying any property values replaces all
        of them. To change one property, fetch the resource and put() it.
        """
        body = json.dumps(data).encode()
        return self.request("PATCH", path, body=body, content_type="application/json")

    def put(self, path, data):
        """Replace a resource with data, typically its own fetched JSON with
        a change made to it."""
        body = json.dumps(data).encode()
        return self.request("PUT", path, body=body, content_type="application/json")

    def post_with_file(self, path, data, file: Path):
        """POST JSON plus one file, as Omeka's upload ingester expects: the
        JSON in a "data" part, the file in "file[0]"."""
        boundary = uuid.uuid4().hex
        mime = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
        body = b"".join(
            [
                f"--{boundary}\r\n".encode(),
                b'Content-Disposition: form-data; name="data"\r\n',
                b"Content-Type: application/json\r\n\r\n",
                json.dumps(data).encode(),
                f"\r\n--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="file[0]"; '
                f'filename="{file.name}"\r\n'.encode(),
                f"Content-Type: {mime}\r\n\r\n".encode(),
                file.read_bytes(),
                f"\r\n--{boundary}--\r\n".encode(),
            ]
        )
        return self.request(
            "POST", path, body=body,
            content_type=f"multipart/form-data; boundary={boundary}",
        )

    def term_id(self, kind: str, term: str) -> int:
        """The id of a property or resource class, from its term, e.g.
        dcterms:title. The API takes ids, and they differ between installs."""
        if (kind, term) not in self._terms:
            found = self.get(kind, term=term)
            if not found:
                raise OmekaError(f"Omeka has no {kind} with the term {term}")
            self._terms[kind, term] = found[0]["o:id"]
        return self._terms[kind, term]

    def find_by_identifier(self, resource: str, identifier: str):
        found = self.get(
            resource,
            **{
                "property[0][property]": "dcterms:identifier",
                "property[0][type]": "eq",
                "property[0][text]": identifier,
            },
        )
        return found[0] if found else None


def values(omeka: Omeka, metadata: dict, directory: Path) -> dict:
    """Turn a manifest's metadata table into Omeka's JSON-LD values.

    A value is a string (a literal), a table with "value" and optionally
    "lang" (a literal in a language), a table with "text_file" (a literal
    read from that file, relative to the collection's directory, for long
    text such as a transcript), or a table with "uri" and optionally "label"
    (a link). Any of them can be given as a list.
    """
    out = {}
    for term, given in metadata.items():
        property_id = omeka.term_id("properties", term)
        entries = []
        for value in given if isinstance(given, list) else [given]:
            if isinstance(value, str):
                value = {"value": value}
            if "text_file" in value:
                text = (directory / value["text_file"]).read_text(encoding="utf-8")
                value = {**value, "value": text.strip()}
            if "uri" in value:
                entry = {"type": "uri", "@id": value["uri"]}
                if "label" in value:
                    entry["o:label"] = value["label"]
            else:
                entry = {"type": "literal", "@value": value["value"]}
                if "lang" in value:
                    entry["@language"] = value["lang"]
            entries.append({"property_id": property_id, **entry})
        out[term] = entries
    return out


def resource(omeka: Omeka, spec: dict, directory: Path) -> dict:
    """The fields an item set and an item share: identifier, class, metadata."""
    data = values(
        omeka, {"dcterms:identifier": spec["identifier"], **spec["metadata"]}, directory
    )
    if "class" in spec:
        data["o:resource_class"] = {"o:id": omeka.term_id("resource_classes", spec["class"])}
    return data


def seed_vocabularies(omeka: Omeka) -> None:
    """Create the vocabularies in collections/vocabularies.toml, for terms the
    collections use that Omeka does not ship with."""
    manifest = tomllib.loads((COLLECTIONS / "vocabularies.toml").read_text())
    for spec in manifest.get("vocabularies", []):
        if omeka.get("vocabularies", prefix=spec["prefix"]):
            print(f"Vocabulary {spec['prefix']}: exists, left unchanged")
            continue
        omeka.post(
            "vocabularies",
            {
                "o:prefix": spec["prefix"],
                "o:namespace_uri": spec["namespace_uri"],
                "o:label": spec["label"],
                "o:comment": spec.get("comment", ""),
                "o:property": [
                    {
                        "o:local_name": prop["local_name"],
                        "o:label": prop["label"],
                        "o:comment": prop.get("comment", ""),
                    }
                    for prop in spec.get("properties", [])
                ],
            },
        )
        print(f"Vocabulary {spec['prefix']}: created")


def seed_site(omeka: Omeka, spec: dict, item_set: dict):
    """A public site showing one item set, with a home page introducing it.

    Created with the item set in its pool, but items are assigned to it
    one by one as they are created, since Omeka 4 shows a site only the items
    assigned to it.
    """
    found = omeka.get("sites", slug=spec["slug"])
    if found and found[0].get("o:homepage"):
        print(f"Site {spec['slug']}: exists, left unchanged")
        return found[0]
    if found:
        # Created, but an interrupted run never gave it its home page.
        site = found[0]
        finish_site(omeka, spec, site)
        print(f"Site {spec['slug']}: existed without a home page; finished")
        return site

    site = omeka.post(
        "sites",
        {
            "o:slug": spec["slug"],
            "o:title": spec["title"],
            "o:summary": spec.get("summary", ""),
            "o:theme": spec.get("theme", "tetrak-reader"),
            "o:is_public": True,
            "o:item_pool": {"item_set_id": [str(item_set["o:id"])]},
            "o:assign_new_items": False,
            "o:site_item_set": [{"o:item_set": {"o:id": item_set["o:id"]}}],
        },
    )
    finish_site(omeka, spec, site)
    print(f"Site {spec['slug']}: created")
    return site


def finish_site(omeka: Omeka, spec: dict, site: dict) -> None:
    """Give a site its home page and navigation: the steps after creating it.

    Separate so that a run interrupted between them can finish the job. A
    home page left by such a run is reused rather than duplicated.
    """
    pages = omeka.get("site_pages", site_id=site["o:id"], per_page=1000)
    home = next((page for page in pages if page["o:slug"] == "home"), None) or omeka.post(
        "site_pages",
        {
            "o:site": {"o:id": site["o:id"]},
            "o:slug": "home",
            "o:title": spec["title"],
            "o:block": [
                {"o:layout": "html", "o:data": {"html": spec["introduction"]}},
                {
                    "o:layout": "browsePreview",
                    "o:data": {
                        "resource_type": "items",
                        "query": "",
                        "heading": "In this collection",
                        "limit": 12,
                        "components": ["resource-heading", "resource-body", "thumbnail"],
                        "link-text": "Browse all",
                    },
                },
            ],
        },
    )
    # Every new site gets an example "Welcome" page; listing only the home
    # page in o:page removes it.
    omeka.patch(
        f"sites/{site['o:id']}",
        {
            "o:page": [{"o:id": home["o:id"]}],
            "o:homepage": {"o:id": home["o:id"]},
            "o:navigation": [
                {"type": "page", "data": {"label": "", "id": home["o:id"]}, "links": []},
                {"type": "browse", "data": {"label": "Browse", "query": ""}, "links": []},
            ],
        },
    )


def seed_collection(omeka: Omeka, directory: Path) -> None:
    manifest = tomllib.loads((directory / "collection.toml").read_text())

    spec = manifest["item_set"]
    item_set = omeka.find_by_identifier("item_sets", spec["identifier"])
    if item_set:
        print(f"Item set {spec['identifier']}: exists, left unchanged")
    else:
        item_set = omeka.post("item_sets", resource(omeka, spec, directory))
        print(f"Item set {spec['identifier']}: created")

    site = seed_site(omeka, manifest["site"], item_set) if "site" in manifest else None

    for spec in manifest["items"]:
        item = omeka.find_by_identifier("items", spec["identifier"])
        if item:
            print(f"  Item {spec['identifier']}: exists")
            # The one change made to an existing item: a site added to the
            # manifest after the item was seeded still gets to show it.
            sites = [s["o:id"] for s in item["o:site"]]
            if site and site["o:id"] not in sites:
                omeka.patch(
                    f"items/{item['o:id']}",
                    {"o:site": [{"o:id": i} for i in [*sites, site["o:id"]]]},
                )
                print(f"  Item {spec['identifier']}: added to site {site['o:slug']}")
        else:
            data = resource(omeka, spec, directory)
            data["o:item_set"] = [{"o:id": item_set["o:id"]}]
            data["o:site"] = [{"o:id": site["o:id"]}] if site else []
            item = omeka.post("items", data)
            print(f"  Item {spec['identifier']}: created")

        # Uploaded one request at a time: a single scan can be several MB.
        existing = {
            media["o:source"]
            for media in omeka.get("media", item_id=item["o:id"], per_page=1000)
        }
        for position, media in enumerate(spec.get("media", []), start=1):
            file = directory / media["file"]
            if file.name in existing:
                continue
            data = values(omeka, media.get("metadata", {}), directory)
            data.update(
                {
                    "o:ingester": "upload",
                    "file_index": 0,
                    "o:item": {"o:id": item["o:id"]},
                    # Explicit, so a resumed run still puts pages in order.
                    "position": position,
                }
            )
            if "alt_text" in media:
                data["o:alt_text"] = media["alt_text"]
            omeka.post_with_file("media", data, file)
            print(f"    {media['file']}: uploaded")


def credentials() -> tuple[str, str, str]:
    settings = {}
    path = key_file()
    if path.exists():
        for line in path.read_text().splitlines():
            key, sep, value = line.partition("=")
            if sep and not key.startswith("#"):
                settings[key.strip()] = value.strip()
    settings.update({k: v for k, v in os.environ.items() if k.startswith("OMEKA_")})
    try:
        return (
            settings["OMEKA_URL"],
            settings["OMEKA_KEY_IDENTITY"],
            settings["OMEKA_KEY_CREDENTIAL"],
        )
    except KeyError as missing:
        sys.exit(
            f"{Path(sys.argv[0]).name}: {missing.args[0]} is not set and there is no "
            f"{path.name} for this instance -- run scripts/install.sh first"
        )


def main(names: list[str]) -> None:
    available = sorted(p.parent.name for p in COLLECTIONS.glob("*/collection.toml"))
    unknown = set(names) - set(available)
    if unknown:
        sys.exit(f"seed.py: no collection named {', '.join(sorted(unknown))}; "
                 f"there are {', '.join(available)}")

    omeka = Omeka(*credentials())
    try:
        seed_vocabularies(omeka)
        for name in names or available:
            seed_collection(omeka, COLLECTIONS / name)
    except OmekaError as error:
        sys.exit(f"seed.py: {error}")


if __name__ == "__main__":
    main(sys.argv[1:])
