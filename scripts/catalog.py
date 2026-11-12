#!/usr/bin/env python3
"""Read-only discovery of all resource tables in public-apis/public-apis.

Python standard library only. Never follows catalog links or runs their commands.
Search scores measure lexical matches, not service quality or availability.
"""

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


SOURCE = "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md"
REPOSITORY = "https://github.com/public-apis/public-apis"
MAX_BYTES = 8 * 1024 * 1024
LINK = re.compile(r"\[([^\]]+)\]\(\s*(https?://[^\s)]+)\s*\)")
TOKEN = re.compile(r"[^\W_]+(?:[-.][^\W_]+)*", re.UNICODE)


def clean(value):
    value = LINK.sub(lambda m: m.group(1), value)
    value = re.sub(r"<[^>]*>", "", value)
    return re.sub(r"\s+", " ", html.unescape(value.replace("`", ""))).strip()


def cells(line):
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def parse_catalog(markdown):
    entries, warnings = [], []
    category, headers = "Uncategorized", None
    fenced = False
    for number, line in enumerate(markdown.splitlines(), 1):
        if re.match(r"^\s*(```|~~~)", line):
            fenced = not fenced
            continue
        if fenced:
            continue
        heading = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if heading:
            category, headers = clean(heading.group(1)), None
            continue
        if "|" not in line:
            headers = None
            continue
        row = cells(line)
        if all(re.fullmatch(r":?-{3,}:?", c) for c in row):
            continue
        labels = [clean(c).casefold() for c in row]
        if "description" in labels and not LINK.search(row[0]):
            headers = labels
            continue
        if not headers:
            if LINK.search(row[0]):
                warnings.append({"line": number, "issue": "Linked table row without a recognized header"})
            continue
        while len(row) > len(headers) and not row[-1]:
            row.pop()
        ambiguous = len(row) != len(headers)
        if ambiguous:
            warnings.append({"line": number, "issue": "Irregular columns; entry retained, verify its raw row"})
        link = LINK.search(row[0])
        if not link:
            warnings.append({"line": number, "issue": "Entry has no readable HTTP(S) link in its first cell"})
            continue
        fields = dict(zip(headers, row + [""] * max(0, len(headers) - len(row))))
        entry = {
            "name": clean(link.group(1)),
            "url": link.group(2),
            "description": clean(fields["description"]),
            "category": category,
            "kind": "mcp" if "transport" in headers else "api",
            "catalog_line": number,
            "catalog_reference": f"{REPOSITORY}/blob/master/README.md#L{number}",
            "catalog_fields": {k: clean(v) for k, v in fields.items() if k != headers[0]},
        }
        related_links = {key: [{"label": clean(m.group(1)), "url": m.group(2)} for m in LINK.finditer(value)]
                         for key, value in fields.items() if key != headers[0] and LINK.search(value)}
        if related_links:
            entry["related_links"] = related_links
        if ambiguous:
            entry["metadata_status"] = "Irregular columns; consult raw row and official docs"
            entry["raw_row"] = line
        entries.append(entry)
    if not entries:
        raise ValueError("No resource tables found. Inspect the README or use web tools; do not report an empty catalog.")
    return entries, warnings


def digest(data):
    return hashlib.sha256(data).hexdigest()


def download():
    request = Request(SOURCE, headers={"User-Agent": "public-apis-advisor/1.0", "Accept": "text/plain"})
    try:
        with urlopen(request, timeout=30) as response:
            if urlsplit(response.geturl()).scheme != "https":
                raise ValueError("Refusing a non-HTTPS catalog redirect")
            data = response.read(MAX_BYTES + 1)
    except URLError:
        # macOS Python may lack a configured CA store; system curl uses its
        # configured trust store. Never disable certificate verification.
        curl = shutil.which("curl")
        if not curl:
            raise
        response = subprocess.run(
            [curl, "--fail", "--location", "--silent", "--show-error",
             "--proto", "=https", "--proto-redir", "=https", "--max-time", "25",
             "--max-filesize", str(MAX_BYTES), "--user-agent", "public-apis-advisor/1.0", SOURCE],
            capture_output=True, timeout=28, check=False,
        )
        if response.returncode:
            raise ValueError("Catalog download failed: " + response.stderr.decode("utf-8", errors="replace").strip())
        data = response.stdout
    if len(data) > MAX_BYTES:
        raise ValueError("Catalog exceeds the 8 MiB limit; inspect the source before proceeding")
    return data, {
        "source_url": SOURCE,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "sha256": digest(data),
        "provider_verification": "Not performed; catalog metadata only",
    }


def load_catalog(readme):
    warnings = []
    if readme:
        path = Path(readme)
        data = path.read_bytes()
        if len(data) > MAX_BYTES:
            raise ValueError("Local catalog exceeds the 8 MiB limit")
        source = {"local_file": str(path.resolve()), "sha256": digest(data), "fetched_at_utc": None}
        sidecar = path.with_name(path.name + ".source.json")
        if sidecar.exists():
            try:
                saved = json.loads(sidecar.read_text(encoding="utf-8"))
                if isinstance(saved, dict) and saved.get("sha256") == source["sha256"]:
                    source.update(saved)
                else:
                    warnings.append({"issue": "Snapshot metadata hash mismatch; fetch time is unknown"})
            except (ValueError, UnicodeError):
                warnings.append({"issue": "Snapshot metadata is unreadable; fetch time is unknown"})
        source["provider_verification"] = "Not performed; catalog metadata only"
    else:
        data, source = download()
    entries, parse_warnings = parse_catalog(data.decode("utf-8-sig"))
    return entries, source, warnings + parse_warnings


def search(entries, query, categories, kind, all_terms):
    known = {entry["category"].casefold(): entry["category"] for entry in entries}
    requested = {category.casefold() for category in categories}
    unknown = requested - known.keys()
    if unknown:
        raise ValueError("Unknown category: " + ", ".join(sorted(unknown)) + ". Run categories to get current names.")
    terms = list(dict.fromkeys(TOKEN.findall(query.casefold())))
    if query.strip() and not terms:
        raise ValueError("Search needs at least one word; use an empty query to browse a category")
    patterns = {term: re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)") for term in terms}
    matches = []
    for entry in entries:
        if requested and entry["category"].casefold() not in requested:
            continue
        if kind != "all" and entry["kind"] != kind:
            continue
        score, found = 0, []
        for term, pattern in patterns.items():
            points = sum(weight for field, weight in (("name", 8), ("description", 3), ("category", 2))
                         if pattern.search(entry[field].casefold()))
            if points:
                score += points
                found.append(term)
        if terms and (not found or (all_terms and len(found) != len(terms))):
            continue
        matches.append({**entry, "matched_terms": found, "lexical_score": score})
    return sorted(matches, key=lambda e: (-len(e["matched_terms"]), -e["lexical_score"], e["name"].casefold(), e["catalog_line"]))


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    fetch = commands.add_parser("fetch", help="Download the official README and source metadata, without following entry links")
    fetch.add_argument("--output", required=True, help="Snapshot path inside the current task's scratch directory")
    for name in ("categories", "search"):
        command = commands.add_parser(name)
        command.add_argument("--readme", help="Use a local README snapshot, without network access")
        if name == "search":
            command.add_argument("query", nargs="?", default="", help="Space-separated terms, matched with OR by default")
            command.add_argument("--category", action="append", default=[], help="Exact category name; repeat for multiple categories")
            command.add_argument("--kind", choices=("all", "api", "mcp"), default="all")
            command.add_argument("--all-terms", action="store_true", help="Require all search terms")
            command.add_argument("--limit", type=positive_int, default=8)
            command.add_argument("--offset", type=int, default=0, help="Row offset for paging through all matches")
    args = parser.parse_args()

    try:
        if args.command == "fetch":
            data, source = download()
            entries, warnings = parse_catalog(data.decode("utf-8-sig"))
            path = Path(args.output)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            path.with_name(path.name + ".source.json").write_text(json.dumps(source, indent=2) + "\n", encoding="utf-8")
            result = {"snapshot": str(path.resolve()), "source": source, "entries": len(entries),
                      "categories": len({entry["category"] for entry in entries}), "warnings": warnings}
        else:
            entries, source, warnings = load_catalog(args.readme)
            result = {"source": source, "catalog_entries": len(entries), "warnings": warnings}
            if args.command == "categories":
                counts = Counter(entry["category"] for entry in entries)
                result["categories"] = [{"name": category, "entries": count} for category, count in counts.items()]
            else:
                if args.offset < 0:
                    raise ValueError("Offset cannot be negative")
                matches = search(entries, args.query, args.category, args.kind, args.all_terms)
                end = args.offset + args.limit
                result.update({"query": args.query, "matched_entries": len(matches), "offset": args.offset,
                               "next_offset": end if end < len(matches) else None,
                               "ranking": "Lexical matches only; not a recommendation or availability check",
                               "results": matches[args.offset:end]})
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, URLError, ValueError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"error": str(error), "action": "Use a valid local --readme snapshot or read the official catalog with web tools. No providers were contacted."}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
