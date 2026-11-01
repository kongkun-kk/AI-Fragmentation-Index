# -*- coding: utf-8 -*-
"""Step 2 - Structured extraction.

Real mode sends each chunk to an OpenAI-compatible chat endpoint and parses the
JSON coding record. Dry-run mode writes deterministic MOCK records (flagged
"mock": true) so the rest of the pipeline can be exercised before any API key or
model is configured. MOCK records must never be used for analysis.

Usage:
    python pipeline/extract.py --chunks data/demo/chunks.jsonl --model mock-a --dry-run --output data/demo/raw_mock_a.jsonl
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

from pipeline.provenance import stamp

DOMAINS = [
    "data_governance",
    "risk_based_ai_regulation",
    "compute_export_controls",
    "model_algorithm_oversight",
    "ai_talent_migration",
]


def mock_record(chunk, model, model_version, prompt_version, schema_version):
    h = int(hashlib.md5((model + "|" + chunk["text"]).encode("utf-8")).hexdigest(), 16)
    return {
        "chunk_id": chunk["chunk_id"],
        "article_ref": chunk.get("article_ref"),
        "applies": True,
        "mock": True,
        "domains": [DOMAINS[h % len(DOMAINS)]],
        "direction": "restrictive" if h % 2 == 0 else "permissive",
        "restrictiveness": round((h % 101) / 100, 2),
        "bindingness": "binding_law",
        "scope": "MOCK - replace with model output",
        "quote": chunk["text"][:120],
        "provenance": stamp(model, model_version, prompt_version, schema_version),
    }


def call_model(client, model, system, chunk):
    user = (
        "Coding fields: applies, domains, direction, restrictiveness (0-1, "
        "rubric-anchored), bindingness, scope, quote (exact provision text "
        "justifying the codes).\n\nProvision text:\n" + chunk["text"]
    )
    resp = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    content = resp.choices[0].message.content
    try:
        parsed = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        parsed = {"applies": None, "parse_error": True, "raw": (content or "")[:500]}
    parsed["provenance"] = stamp(model, "unspecified", "v1", "v1")
    return parsed


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--chunks", required=True, help="JSONL from chunker/chunk.py")
    ap.add_argument("--output", required=True)
    ap.add_argument("--model", required=True, help="model name recorded in provenance")
    ap.add_argument("--model-version", default="unspecified")
    ap.add_argument("--prompt-version", default="v1")
    ap.add_argument("--schema-version", default="v1")
    ap.add_argument("--system-prompt", default="prompts/system_prompt.md")
    ap.add_argument("--dry-run", action="store_true", help="write MOCK records; no API call")
    args = ap.parse_args()

    chunks = [
        json.loads(line)
        for line in Path(args.chunks).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if args.dry_run:
        records = [
            mock_record(c, args.model, args.model_version, args.prompt_version, args.schema_version)
            for c in chunks
        ]
    else:
        try:
            from openai import OpenAI
        except ImportError:
            sys.exit("openai package not installed; run: pip install openai  (or use --dry-run)")
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        if not api_key:
            sys.exit("OPENAI_API_KEY not set; copy .env.example to .env and fill it in (or use --dry-run)")
        client = OpenAI(api_key=api_key, base_url=base_url)
        system_path = Path(args.system_prompt)
        system = system_path.read_text(encoding="utf-8") if system_path.exists() else ""
        records = []
        for chunk in chunks:
            parsed = call_model(client, args.model, system, chunk)
            records.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "article_ref": chunk.get("article_ref"),
                    **parsed,
                }
            )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("wrote %d records to %s" % (len(records), args.output))


if __name__ == "__main__":
    main()
