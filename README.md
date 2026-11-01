# AI Fragmentation

An AI-enabled measurement of cross-national AI regulation ("AI fragmentation in a
multipolar world") and a reusable, schema-driven legal-coding infrastructure, with a
demonstration application to MNE AI capability transfer.

Repository: https://github.com/kongkun-kk/AI-Fragmentation-Index

> **Status (2026-11): work in progress.** This repository accompanies the Stage 1
> research proposal submitted to the Organization Science special issue
> "AI-Enabled Frontiers in Organizational Science". LLM coding of legal provisions
> is underway; inter-coder agreement statistics are not yet available; the MNE
> panel is under construction. Anything produced in --dry-run mode is MOCK data
> for pipeline testing only and must never be used for analysis.

## What this repository is

1. **A new measure.** A versioned database in which every provision of national
   AI-related legal instruments is coded by LLMs under human audit and aggregated
   into five domain-level restrictiveness scores, a country-level AI Fragmentation
   Index, and dyadic HQ-host policy alignment measures.
2. **A reusable infrastructure.** The coding workflow is corpus-agnostic: replacing
   the schema and rubric re-targets it to any legal domain (data protection, labor
   law, FDI screening, export controls). It ships as an open-source Python package
   plus a gold-standard benchmark corpus.
3. **A demonstration application.** An MNE subsidiary panel studying whether HQ AI
   capability transfers to foreign subsidiaries through AI talent recruitment and
   mobility (code for that study lives in a separate private repository because of
   person-level data; only aggregated and synthetic outputs will be shared here).

## The six-step coding protocol

1. **Chunking** - split instruments into provision-level chunks; the chunk map is
   human-verified.
2. **Structured extraction** - each chunk is coded by an LLM constrained to the
   schema (JSON-schema/function calling, temperature 0), with rubric anchors and
   negative examples; codes must be grounded in the verbatim provision text.
3. **Multi-model ensembling** - at least three models (one open-weight, at least
   two frontier API models); disagreements go to adjudication, not silent averaging.
4. **Self-verification** - the model re-reads its codes against the quoted spans;
   failures loop back to Step 2.
5. **Human audit** - a stratified sample per country-domain-year cell is
   double-coded by two trained human coders; human-human and human-AI agreement
   (Krippendorff's alpha) are reported; adjudications follow a written rulebook and
   feed back into prompt refinement.
6. **Versioning** - every code records model, model version, prompt version,
   schema version, date, and auditor.

See docs/PROTOCOL.md for the full protocol.

## Repository structure

    ai-fragmentation/
    |-- README.md                this file
    |-- LICENSE                  MIT (code)
    |-- DATA_LICENSE.md          CC BY 4.0 (data, benchmark corpus)
    |-- CITATION.cff             citation metadata
    |-- .gitignore
    |-- .env.example             API key template (never commit .env)
    |-- pyproject.toml           package metadata and dependencies
    |-- requirements.txt         pip-compatible dependency list
    |-- schema/
    |   |-- coding_schema.json   JSON Schema of the coding record
    |   |-- rubrics.md           per-domain definitions and 0-1 restrictiveness anchors
    |-- prompts/
    |   |-- system_prompt.md     versioned system prompt
    |   |-- few_shot_examples.md illustrative examples (fictional text)
    |-- chunker/
    |   |-- chunk.py             Step 1: provision-level chunking
    |   |-- example_input.txt    FICTIONAL sample text for testing only
    |-- pipeline/
    |   |-- extract.py           Step 2: LLM extraction (has --dry-run mock mode)
    |   |-- ensemble.py          Step 3: multi-model ensembling
    |   |-- verify.py            Step 4: self-verification (stub, loop-back hook)
    |   |-- audit.py             Step 5: human audit sample generator
    |   |-- provenance.py        provenance helpers (versions, timestamps, git SHA)
    |-- data/
    |   |-- registry/
    |   |   |-- instrument_registry_template.csv   provenance ledger for instruments
    |   |-- raw/                 raw per-model outputs (gitignored, .gitkeep kept)
    |   |-- codes/               adjudicated versioned codes (gitignored)
    |   |-- index/               aggregated index outputs (gitignored)
    |-- index/
    |   |-- aggregate.py         domain scores, dyadic alignment, fragmentation index
    |-- config/
    |   |-- config.json          domain weights, tolerances, bloc assignments
    |-- benchmark/
    |   |-- README.md            what the gold standard is and how to extend it
    |   |-- gold_standard_template.csv
    |   |-- example_human_codes.csv   synthetic example for the reliability script
    |-- validation/
    |   |-- reliability.py       percent agreement, Scott's pi, Cohen's kappa,
    |   |                        Krippendorff's alpha (via the krippendorff package)
    |   |-- tracker_benchmark.py instrument-level benchmark vs White & Case/OECD.AI
    |-- docs/
    |   |-- PROTOCOL.md          full six-step protocol
    |   |-- REPRODUCIBILITY.md   pins, seeds, model versions, data policy
    |-- scripts/
    |   |-- run_demo.py          end-to-end dry-run demo
    |-- .github/
        |-- workflows/
            |-- ci.yml          CI smoke test running the demo

## Quickstart (no data, no API keys needed)

Run all commands from the repository root. Either install the package first
(pip install -e .), or set PYTHONPATH=. so the pipeline package is importable.

    pip install -e .

    # single command: chunk -> extract (mock) -> ensemble -> aggregate -> reliability
    python scripts/run_demo.py

    # or step by step
    python chunker/chunk.py chunker/example_input.txt --instrument-id EX_AI_2024 --output data/demo/chunks.jsonl
    python pipeline/extract.py --chunks data/demo/chunks.jsonl --model mock-a --dry-run --output data/demo/raw_mock_a.jsonl
    python pipeline/extract.py --chunks data/demo/chunks.jsonl --model mock-b --dry-run --output data/demo/raw_mock_b.jsonl
    python pipeline/extract.py --chunks data/demo/chunks.jsonl --model mock-c --dry-run --output data/demo/raw_mock_c.jsonl
    python pipeline/ensemble.py --inputs data/demo/raw_mock_a.jsonl data/demo/raw_mock_b.jsonl data/demo/raw_mock_c.jsonl --output data/demo/consensus.jsonl
    python index/aggregate.py --input data/demo/consensus.jsonl --config config/config.json --output-dir data/demo/index --year 2024
    python validation/reliability.py --input benchmark/example_human_codes.csv --value-col value --metric nominal

All demo outputs go to data/demo/ (gitignored). Every mock record is flagged
with "mock": true and must not enter any analysis.

## Running real models

1. Copy .env.example to .env and fill in at least one API key.
2. Register each instrument in data/registry/instrument_registry_template.csv
   (country, instrument type, effective dates, official URL, retrieval date,
   language). The registry is the data provenance ledger: prefer storing official
   URLs over full texts wherever licenses are unclear.
3. Run the steps with real models, bumping --prompt-version and --schema-version
   on every change:

    python pipeline/extract.py --chunks data/.../chunks.jsonl --model gpt-4o-mini --model-version 2025-01-01 --output data/raw/gpt-4o-mini_v1.jsonl

4. After ensembling, generate the audit sample and have two coders fill it in:

    python pipeline/audit.py --input data/codes/consensus.jsonl --output data/codes/audit_sample.csv --frac 0.1 --seed 42
    python validation/reliability.py --input data/codes/audit_sample_human.csv --value-col final_restrictiveness --metric interval

## Data policy and ethics

- Only public legal texts are coded; where licenses are unclear the repository
  stores official links, not full texts.
- No person-level data (LinkedIn/Revelio/LinkUp) is stored or redistributed; only
  aggregated measures and synthetic data will be published, per the special
  issue's guidance.
- Every code carries provenance (model, model version, prompt version, schema
  version, timestamp, auditor) so the database can be re-run and audited.

## Reproducibility

See docs/REPRODUCIBILITY.md. Key points: model versions are pinned per release;
temperature is 0; the open-weight anchor model and the public benchmark corpus
allow full replication of the protocol even if proprietary API access changes.

## Roadmap (Stage 2, Jan-May 2027)

- Complete the corpus for 40+ economies; finish double-coding, adjudication, and
  tracker benchmarking.
- Release the package publicly with documentation and a replication recipe.
- Complete the dyadic panel and the difference-in-differences application.
- Integrate feedback from the February 2027 workshop.

## License

- Code: MIT (see LICENSE).
- Data, schema, rubrics, prompts, and the benchmark corpus: CC BY 4.0 (see
  DATA_LICENSE.md). Legal texts themselves remain official/public documents and
  are linked, not redistributed.

## Citation

See CITATION.cff, or cite:

    Kong, K., Yuan, L., & Chen, X. (2026). Measuring AI fragmentation in a
    multipolar world: An AI-enabled legal-coding infrastructure (Version 0.1.0)
    [Computer software and data]. https://github.com/kongkun-kk/AI-Fragmentation-Index

## Contact

Replace with the corresponding author's email. (Kun Kong, University of Macau;
Lin Yuan (corresponding), University of Macau.)
