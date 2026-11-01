# -*- coding: utf-8 -*-
"""Step 3 - Multi-model ensembling.

Merge per-model raw outputs into a consensus record. Votes are retained per
model; disagreements (different domain sets, restrictiveness spread beyond the
tolerance, or applies conflicts) set needs_adjudication=true and are resolved
in human adjudication, never silently averaged away.

Usage:
    python pipeline/ensemble.py --inputs data/demo/raw_mock_a.jsonl data/demo/raw_mock_b.jsonl data/demo/raw_mock_c.jsonl --output data/demo/consensus.jsonl
"""
import argparse
import json
from collections import Counter
from pathlib import Path


def load(path):
    rows = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        rows[r["chunk_id"]] = r
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inputs", nargs="+", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--tolerance", type=float, default=0.15,
                    help="max spread in restrictiveness before adjudication is flagged")
    args = ap.parse_args()

    per_model = [load(p) for p in args.inputs]
    chunk_ids = []
    for m in per_model:
        for cid in m:
            if cid not in chunk_ids:
                chunk_ids.append(cid)

    out = []
    for cid in chunk_ids:
        votes = []
        for rows in per_model:
            r = rows.get(cid)
            if r is None:
                continue
            prov = r.get("provenance") or {}
            votes.append(
                {
                    "model": prov.get("model", r.get("model", "?")),
                    "applies": r.get("applies"),
                    "domains": tuple(sorted(r.get("domains") or [])),
                    "restrictiveness": r.get("restrictiveness"),
                }
            )
        applies = [v["applies"] for v in votes]
        doms = Counter(v["domains"] for v in votes if v["domains"])
        consensus_domains = list(doms.most_common(1)[0][0]) if doms else []
        rvals = [v["restrictiveness"] for v in votes if isinstance(v["restrictiveness"], (int, float))]
        consensus_r = round(sum(rvals) / len(rvals), 3) if rvals else None
        spread = (max(rvals) - min(rvals)) if len(rvals) > 1 else 0.0
        needs_adj = (
            len(doms) > 1
            or spread > args.tolerance
            or None in applies
            or len(set(applies)) > 1
        )
        out.append(
            {
                "chunk_id": cid,
                "consensus_applies": bool(any(a is True for a in applies)),
                "consensus_domains": consensus_domains,
                "consensus_restrictiveness": consensus_r,
                "votes": votes,
                "needs_adjudication": bool(needs_adj),
            }
        )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for rec in out:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    flagged = sum(1 for rec in out if rec["needs_adjudication"])
    print("wrote %d consensus records to %s (%d flagged for adjudication)" % (len(out), args.output, flagged))


if __name__ == "__main__":
    main()
