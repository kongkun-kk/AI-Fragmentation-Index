# -*- coding: utf-8 -*-
"""End-to-end dry-run demo.

Chunks the fictional example text, runs three MOCK model extractions (no API
calls), ensembles them, aggregates the index, and runs the reliability script on
the synthetic human-codes example. All outputs go to data/demo/ (gitignored).
MOCK records are flagged "mock": true and must never be used for analysis.

Usage:
    python scripts/run_demo.py
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PY = sys.executable


def run(args):
    print("$", " ".join(args))
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    subprocess.run([PY] + args, cwd=ROOT, env=env, check=True)


def main():
    demo = ROOT / "data" / "demo"
    run(["chunker/chunk.py", "chunker/example_input.txt",
         "--instrument-id", "EX_AI_2024", "--output", str(demo / "chunks.jsonl")])
    for model in ("mock-a", "mock-b", "mock-c"):
        run(["pipeline/extract.py", "--chunks", str(demo / "chunks.jsonl"),
             "--model", model, "--dry-run", "--output", str(demo / ("raw_%s.jsonl" % model))])
    run(["pipeline/ensemble.py",
         "--inputs", str(demo / "raw_mock-a.jsonl"), str(demo / "raw_mock-b.jsonl"), str(demo / "raw_mock-c.jsonl"),
         "--output", str(demo / "consensus.jsonl")])
    run(["pipeline/verify.py", "--input", str(demo / "consensus.jsonl"),
         "--output", str(demo / "consensus_verified.jsonl")])
    run(["pipeline/audit.py", "--input", str(demo / "consensus.jsonl"),
         "--output", str(demo / "audit_sample.csv"), "--frac", "0.4", "--seed", "42"])
    run(["index/aggregate.py", "--input", str(demo / "consensus.jsonl"),
         "--config", "config/config.json", "--output-dir", str(demo / "index"), "--year", "2024"])
    run(["validation/reliability.py", "--input", "benchmark/example_human_codes.csv",
         "--value-col", "value", "--metric", "nominal"])
    print("\nDemo finished. Inspect data/demo/ for outputs (all MOCK).")


if __name__ == "__main__":
    main()
