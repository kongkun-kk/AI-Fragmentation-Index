# Reproducibility

## Environment

    pip install -e .
    cp .env.example .env   # fill in API keys

Python >= 3.10; pinned model versions below are recorded in every code's
provenance block.

## Model and version pins

- Open-weight anchor model: Qwen2.5-32B-Instruct (or the closest available
  Llama/Qwen-class model); pin the exact quantization and revision per release.
- Frontier API models: at least two, with provider model snapshots pinned per
  release (record the provider's model version, not just the alias).
- Temperature 0 everywhere; any seedable step uses --seed 42 by convention.

## Versioned inputs

- Prompt version: prompts/system_prompt.md carries a version tag; bump it on
  every change and pass --prompt-version to the pipeline.
- Schema version: schema/coding_schema.json and schema/rubrics.md; bump and pass
  --schema-version.
- Every raw output keeps per-model JSONL under data/raw/ (gitignored) with full
  provenance, so consensus and adjudication can be re-derived from raw outputs.

## Data access policy

- Legal texts are public official documents; the repository stores links and
  metadata (data/registry/) rather than full texts where redistribution is
  unclear.
- Person-level talent data (LinkUp, LinkedIn/Revelio) are never shared; only
  aggregated measures and synthetic data are published, per the special issue's
  guidance.
- The public benchmark corpus (benchmark/) uses public-domain instruments only.

## Rerun policy

Any change to the schema, rubrics, prompts, or a model version triggers a
versioned re-run of the affected corpus; consensus and index outputs always
reference the input versions they were derived from.

## Known limitations (work in progress)

- Self-verification (Step 4) is a stub.
- Registry join in aggregation is minimal; the full country-domain-year
  stratification for audit sampling is not yet wired.
- Agreement statistics are pending completion of the first double-coding round.
