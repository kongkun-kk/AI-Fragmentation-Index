# Benchmark corpus (gold standard)

Human-coded gold standards: provision-level codes produced by two trained human
coders with adjudicated disagreements, treated as reference truth for validating
model outputs and for benchmarking any coding pipeline.

## How to extend

1. Draw provisions from your corpus (public-domain instruments only for the
   public benchmark; see DATA_LICENSE.md).
2. Two coders fill the template independently (columns coder_1_* / coder_2_*).
3. Adjudicate disagreements under the written rulebook (docs/PROTOCOL.md) and
   record the final decision.
4. Add the adjudicated row to gold_standard.csv (rename the template).
5. Report human-human and human-AI agreement with validation/reliability.py.

gold_standard_template.csv columns:
provision_id, instrument_id, country, domain, direction, restrictiveness,
bindingness, scope, quote, coder_1, coder_2, adjudicator, final_decision
