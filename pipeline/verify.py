# -*- coding: utf-8 -*-
"""Step 4 - Self-verification (stub).

Real implementation: for every consensus record, re-send the codes together with
the quoted span to the model and ask it to confirm or revise; records the model
cannot confirm are sent back to Step 2 (needs_re_extraction=true).

This stub keeps the loop-back hook in place and passes records through so the
pipeline remains runnable while the real verification prompt is finalized.

Usage:
    python pipeline/verify.py --input data/demo/consensus.jsonl --output data/demo/consensus_verified.jsonl
"""
import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--dry-run", action="store_true",
                    help="pass through without calling a model (default behaviour for now)")
    args = ap.parse_args()

    rows = [
        json.loads(line)
        for line in Path(args.input).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for rec in rows:
        rec["self_verification"] = {"status": "stub", "needs_re_extraction": False}

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for rec in rows:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("wrote %d records to %s (self-verification is a stub)" % (len(rows), args.output))


if __name__ == "__main__":
    main()
