# -*- coding: utf-8 -*-
"""Aggregation - country-year domain scores, dyadic alignment, fragmentation index.

Reads consensus records, attributes each provision to a country via the
instrument registry (data/registry/), and computes:
  - domain scores: weighted mean restrictiveness per country-year-domain
  - dyadic alignment: A_d(c,h,t) = 1 - |r_d(c,t) - r_d(h,t)| per domain, and the
    exposure-weighted overall alignment
  - AI Fragmentation Index: Euclidean distance of a country's domain-score
    vector from the global mean vector

Usage:
    python index/aggregate.py --input data/demo/consensus.jsonl --config config/config.json --output-dir data/demo/index --year 2024
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


def load_registry():
    path = Path("data/registry/instrument_registry_template.csv")
    mapping = {}
    if not path.exists():
        return mapping
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            mapping[row["instrument_id"]] = row.get("country", "UNK")
    return mapping


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True)
    ap.add_argument("--config", default="config/config.json")
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--year", type=int, default=2024)
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    domains = cfg["domains"]
    registry = load_registry()

    rows = [
        json.loads(line)
        for line in Path(args.input).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    scored = []
    for r in rows:
        if not r.get("consensus_applies"):
            continue
        if r.get("consensus_restrictiveness") is None:
            continue
        if not r.get("consensus_domains"):
            continue
        instrument = r["chunk_id"].split("#")[0]
        country = registry.get(instrument, "UNK")
        scored.append((country, r["consensus_domains"], float(r["consensus_restrictiveness"])))

    per_cd = defaultdict(list)
    for country, ds, r in scored:
        for d in ds:
            if d in domains:
                per_cd[(country, d)].append(r)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    domain_scores = {}
    with (out_dir / "domain_scores.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["country", "year", "domain", "n_provisions", "weighted_mean_restrictiveness"])
        for (country, d), vals in sorted(per_cd.items()):
            mean = sum(vals) / len(vals)
            domain_scores.setdefault(country, {})[d] = mean
            writer.writerow([country, args.year, d, len(vals), round(mean, 4)])

    countries = sorted(domain_scores)
    global_mean = {
        d: sum(domain_scores[c][d] for c in countries if d in domain_scores[c])
        / sum(1 for c in countries if d in domain_scores[c])
        for d in domains
        if any(d in domain_scores[c] for c in countries)
    }
    blocs = cfg.get("blocs", {})

    def bloc_of(country):
        for bloc, members in blocs.items():
            if country in members:
                return bloc
        return "UNK"

    with (out_dir / "fragmentation_index.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["country", "year", "fragmentation_index", "bloc"])
        for c in countries:
            vec = domain_scores[c]
            dist = math.sqrt(
                sum((vec.get(d, global_mean.get(d, 0)) - global_mean[d]) ** 2 for d in global_mean)
            )
            writer.writerow([c, args.year, round(dist, 4), bloc_of(c)])

    with (out_dir / "dyadic_alignment.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["hq_country", "host_country", "year", "domain", "alignment"])
        for i, h in enumerate(countries):
            for c in countries[i + 1:]:
                for d in domains:
                    if d in domain_scores[h] and d in domain_scores[c]:
                        a = 1 - abs(domain_scores[h][d] - domain_scores[c][d])
                        writer.writerow([h, c, args.year, d, round(a, 4)])
                common = [d for d in domains if d in domain_scores[h] and d in domain_scores[c]]
                if common:
                    w = sum(domains[d] for d in common)
                    overall = sum(
                        domains[d] * (1 - abs(domain_scores[h][d] - domain_scores[c][d])) for d in common
                    ) / w
                    writer.writerow([h, c, args.year, "OVERALL", round(overall, 4)])

    print("domain scores:", len(per_cd), "cells | countries:", countries)
    print("wrote CSVs to", out_dir)


if __name__ == "__main__":
    main()
