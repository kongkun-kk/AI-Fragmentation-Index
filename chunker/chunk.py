# -*- coding: utf-8 -*-
"""Step 1 - Chunking.

Split a legal text into provision-level chunks. Output is JSONL with one record
per chunk: {chunk_id, article_ref, text}. The chunk map must be human-verified
before coding (see docs/PROTOCOL.md).

Usage:
    python chunker/chunk.py chunker/example_input.txt --instrument-id EX_AI_2024 --output data/demo/chunks.jsonl
"""
import argparse
import json
import re
from pathlib import Path

ARTICLE_RE = re.compile(
    r"^\s*(?:Article|Art\.?|Section|Sec\.?|Clause|\u00a7)\s+([0-9]+[A-Za-z]?(?:\([0-9]+\))?)\.?\s*(.*)$",
    re.IGNORECASE,
)
ITEM_RE = re.compile(r"^\s*(?:\(([0-9]+)\)|([0-9]+)\.)\s+(.*)$")


def split_provisions(text, instrument_id, min_chars=40):
    chunks = []
    current = None
    last_article = None

    def flush():
        nonlocal current
        if current is not None and current["text"].strip():
            chunks.append(dict(current))
        current = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        am = ARTICLE_RE.match(raw)
        if am:
            flush()
            last_article = am.group(1)
            body = am.group(2).strip()
            if body:
                chunks.append({"article_ref": "Article %s" % last_article, "text": body})
            else:
                current = {"article_ref": "Article %s" % last_article, "text": ""}
            continue
        im = ITEM_RE.match(raw)
        if im and last_article:
            num = im.group(1) or im.group(2)
            body = im.group(3).strip()
            if body:
                flush()
                chunks.append(
                    {"article_ref": "Article %s, para (%s)" % (last_article, num), "text": body}
                )
            continue
        if current is not None:
            current["text"] = (current["text"] + " " + line).strip()
    flush()
    out = []
    for i, c in enumerate(chunks):
        if len(c["text"]) >= min_chars:
            out.append(
                {
                    "chunk_id": "%s#%03d" % (instrument_id, i + 1),
                    "article_ref": c["article_ref"],
                    "text": c["text"],
                }
            )
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", help="plain-text legal document")
    ap.add_argument("--instrument-id", required=True, help="registry instrument id")
    ap.add_argument("--output", required=True, help="output JSONL path")
    ap.add_argument("--min-chars", type=int, default=40)
    args = ap.parse_args()
    text = Path(args.input).read_text(encoding="utf-8")
    chunks = split_provisions(text, args.instrument_id, args.min_chars)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print("wrote %d chunks to %s" % (len(chunks), args.output))


if __name__ == "__main__":
    main()
