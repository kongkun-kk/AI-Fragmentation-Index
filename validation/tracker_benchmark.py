# -*- coding: utf-8 -*-
"""Instrument-level benchmark against hand-maintained trackers (Step 5 support).

Compares the instrument registry with an exported tracker CSV (White & Case AI
Watch, OECD.AI Policy Navigator). Expected tracker CSV columns:
    instrument_id, exists_in_tracker (0/1), tracker_form (e.g. binding law /
    soft law), tracker_bindingness (binding / non-binding)

Our registry supplies instrument_id, country, instrument_name, type. Agreement
is computed on existence, form, and bindingness for instruments shared between
the two files. This is a skeleton: wire in your real tracker exports under
data/registry/ and extend the column mapping as needed.

Usage:
    python validation/tracker_benchmark.py --demo
    python validation/tracker_benchmark.py --registry data/registry/instrument_registry_template.csv --tracker data/registry/whitecase_export.csv
"""
import argparse
import csv


def demo():
    print("Expected tracker CSV format (create e.g. data/registry/whitecase_export.csv):")
    print("  instrument_id,exists_in_tracker,tracker_form,tracker_bindingness")
    print("  EU_AI_ACT,1,binding law,binding")
    print("  CN_GENAI,1,administrative measure,binding")
    print("Agreement will be reported for existence, form, and bindingness.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registry", default=None)
    ap.add_argument("--tracker", default=None)
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    if args.demo or not (args.registry and args.tracker):
        demo()
        return

    registry = {}
    with open(args.registry, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            registry[row["instrument_id"]] = row

    tracker = {}
    with open(args.tracker, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            tracker[row["instrument_id"]] = row

    shared = sorted(set(registry) & set(tracker))
    if not shared:
        print("No instruments shared between the two files.")
        return

    def agree(key_a, key_b, test=lambda a, b: str(a).strip().lower() == str(b).strip().lower()):
        total = hits = 0
        for iid in shared:
            a = registry[iid].get(key_a, "")
            b = tracker[iid].get(key_b, "")
            if a and b:
                total += 1
                hits += int(test(a, b))
        return hits / total if total else None

    existence = agree("exists_in_tracker", "exists_in_tracker")
    form = agree("type", "tracker_form")
    bindingness = agree("type", "tracker_bindingness")
    print("shared instruments:", len(shared))
    print("existence agreement :", round(existence, 4) if existence is not None else "n/a")
    print("form agreement      :", round(form, 4) if form is not None else "n/a")
    print("bindingness agreement:", round(bindingness, 4) if bindingness is not None else "n/a")


if __name__ == "__main__":
    main()
