# -*- coding: utf-8 -*-
"""Inter-coder reliability for the human audit (Step 5).

Input: CSV in long format with columns unit_id, coder, and a value column
(rename with --value-col). Missing values are skipped.

Two-coder case (the default in this project):
  - percent agreement
  - Scott's pi - which equals Krippendorff's alpha for two coders with nominal
    data - and Cohen's kappa (nominal metric)
For interval metrics, ordinal metrics, or more than two coders, install the
reference implementation (pip install krippendorff) and this script will use it.

Usage:
    python validation/reliability.py --input benchmark/example_human_codes.csv --value-col value --metric nominal
"""
import argparse
import csv
from collections import Counter, defaultdict


def load(path, value_col):
    units = defaultdict(dict)
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            v = (row.get(value_col) or "").strip()
            if v == "":
                continue
            units[row["unit_id"]][row["coder"]] = v
    return units


def two_coder_stats(units):
    coders = sorted({c for d in units.values() for c in d})
    if len(coders) != 2:
        return None, coders
    c1, c2 = coders
    agree = total = 0
    m1, m2 = Counter(), Counter()
    for d in units.values():
        if c1 in d and c2 in d:
            total += 1
            v1, v2 = d[c1], d[c2]
            m1[v1] += 1
            m2[v2] += 1
            agree += int(v1 == v2)
    if total == 0:
        return None, coders
    p_o = agree / total
    cats = set(m1) | set(m2)
    p_e_pi = sum(((m1[c] + m2[c]) / (2 * total)) ** 2 for c in cats)
    pi = (p_o - p_e_pi) / (1 - p_e_pi) if p_e_pi < 1 else None
    p_e_k = sum((m1[c] / total) * (m2[c] / total) for c in cats)
    kappa = (p_o - p_e_k) / (1 - p_e_k) if p_e_k < 1 else None
    stats = {
        "n_units": total,
        "coders": coders,
        "percent_agreement": round(p_o, 4),
        "scotts_pi_nominal": round(pi, 4) if pi is not None else None,
        "cohens_kappa_nominal": round(kappa, 4) if kappa is not None else None,
    }
    return stats, coders


def krippendorff_package(units, metric):
    try:
        import krippendorff
    except ImportError:
        return None
    coders = sorted({c for d in units.values() for c in d})
    unit_ids = sorted(units)
    matrix = []
    for uid in unit_ids:
        matrix.append([units[uid].get(c) for c in coders])
    try:
        alpha = krippendorff.alpha(
            reliability_data=matrix,
            level_of_measurement=metric,
        )
        return round(float(alpha), 4)
    except Exception as exc:
        print("krippendorff package call failed:", exc)
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True)
    ap.add_argument("--value-col", default="value")
    ap.add_argument("--metric", default="nominal", choices=["nominal", "ordinal", "interval", "ratio"])
    args = ap.parse_args()

    units = load(args.input, args.value_col)
    stats, coders = two_coder_stats(units)
    if stats:
        print("Two-coder reliability (%s; %d units):" % (" vs ".join(coders), stats["n_units"]))
        print("  percent agreement        :", stats["percent_agreement"])
        print("  Scott's pi (= alpha_nominal):", stats["scotts_pi_nominal"])
        print("  Cohen's kappa (nominal)  :", stats["cohens_kappa_nominal"])
    else:
        print("Detected %d coders; two-coder closed forms do not apply." % len(coders))

    alpha = krippendorff_package(units, args.metric)
    if alpha is not None:
        print("  Krippendorff's alpha (%s): %s" % (args.metric, alpha))
    elif stats:
        print("  Krippendorff's alpha (%s): install the reference implementation with 'pip install krippendorff'" % args.metric)


if __name__ == "__main__":
    main()
