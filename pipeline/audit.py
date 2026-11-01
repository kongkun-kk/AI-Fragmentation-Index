# -*- coding: utf-8 -*-
"""Step 5 - Human audit sample generator.

Draws a stratified random sample from consensus records and writes a CSV that
two human coders fill in (coder_1, coder_2) before adjudication. Grouping is by
instrument for now; TODO: stratify by country-domain-year once the registry join
is wired into the pipeline (see data/registry/).

Usage:
    python pipeline/audit.py --input data/demo/consensus.jsonl --output data/demo/audit_sample.csv --frac 0.3 --seed 42
"""
import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

FIELDS = [
    "chunk_id", "article_ref", "consensus_domains", "consensus_restrictiveness",
    "quote", "coder_1_domains", "coder_1_restrictiveness", "coder_2_domains",
    "coder_2_restrictiveness", "adjudicator", "final_domains",
    "final_restrictiveness", "notes",
]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--frac", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rows = [
        json.loads(line)
        for line in Path(args.input).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    by_instrument = defaultdict(list)
    for r in rows:
        instrument = r["chunk_id"].split("#")[0]
        by_instrument[instrument].append(r)

    rng = random.Random(args.seed)
    sample = []
    for instrument, group in by_instrument.items():
        k = max(1, int(round(len(group) * args.frac)))
        sample.extend(rng.sample(group, min(k, len(group))))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for r in sorted(sample, key=lambda x: x["chunk_id"]):
            writer.writerow(
                {
                    "chunk_id": r["chunk_id"],
                    "article_ref": r.get("article_ref", ""),
                    "consensus_domains": ";".join(r.get("consensus_domains") or []),
                    "consensus_restrictiveness": r.get("consensus_restrictiveness"),
                    "quote": "",
                    "coder_1_domains": "",
                    "coder_1_restrictiveness": "",
                    "coder_2_domains": "",
                    "coder_2_restrictiveness": "",
                    "adjudicator": "",
                    "final_domains": "",
                    "final_restrictiveness": "",
                    "notes": "",
                }
            )
    print("wrote %d sampled provisions to %s" % (len(sample), args.output))


if __name__ == "__main__":
    main()
