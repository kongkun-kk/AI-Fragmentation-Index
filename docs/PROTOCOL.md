# Coding protocol

Full description of the six-step, scripted and logged protocol used to produce
the AI fragmentation measurement. Corresponds to Section 2 of the Stage 1
proposal.

## Step 1 - Chunking

Each instrument is split into provision-level chunks (legal-numbering
heuristics: Article/Section/Clause/paragraph patterns) with chunker/chunk.py.
The chunk map is human-verified before coding.

## Step 2 - Structured extraction

Each chunk is coded by an LLM constrained to the schema
(schema/coding_schema.json) via JSON-schema or function calling, at temperature
0, with rubric anchors and negative examples in the system prompt
(prompts/system_prompt.md). The model must output codes grounded in the
verbatim provision text (the quote field). Script: pipeline/extract.py.

## Step 3 - Multi-model ensembling

Each chunk is coded by at least three models: one open-weight anchor and at
least two frontier API models. Votes are retained per model; disagreements
(domain sets, restrictiveness spread beyond the tolerance, applies conflicts)
set needs_adjudication and are resolved in Step 5, never silently averaged.
Script: pipeline/ensemble.py.

## Step 4 - Self-verification

The model re-reads its codes against the quoted spans and confirms or revises
them; failures loop back to Step 2. Script: pipeline/verify.py (stub; the
verification prompt is being finalized).

## Step 5 - Human audit

A stratified random sample of provisions per country-domain-year cell (share
fixed by design before coding begins) is double-coded by two trained human
coders, with native-language support where needed. We report human-human and
human-AI agreement (Krippendorff's alpha; see validation/reliability.py) and
adjudicate disagreements under a written rulebook; adjudications feed back into
prompt refinement. Script: pipeline/audit.py generates the sample.

## Step 6 - Versioning

Every code records model, model version, prompt version, schema version,
timestamp, git SHA, and auditor (pipeline/provenance.py), so the database can
be re-run and audited after any change. Any model or prompt change triggers a
versioned re-run of the affected corpus.

## Aggregation

Provision codes aggregate into country-year domain scores (weighted by
provision relevance; categorical dimensions use similarity matrices). The AI
Fragmentation Index is a country-year's distance from the global mean domain
vector, and dyadic HQ-host alignment is 1 minus the normalized absolute domain
difference, with weights scaled to a firm's exposure profile. A bloc indicator
(EU/EEA, US-aligned, China-aligned) comes from unsupervised clustering of
regulatory-text embeddings, validated against expert bloc assignments. Script:
index/aggregate.py; weights and bloc assignments in config/config.json.

## Validation

- Human-coded gold standards: benchmark/ (provision-level reference truth).
- Hand-maintained trackers: White & Case AI Watch and OECD.AI Policy Navigator
  (instrument existence, form, bindingness); validation/tracker_benchmark.py.
- Expert surveys on selected country-years (procedure TBD).
