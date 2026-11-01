# Coding rubrics (v1)

Versioned coding rules for the five domains. Update the version tag in
.env / provenance whenever this file changes. Coders (human and LLM) must
anchor every restrictiveness score to the 0 / 0.5 / 1 descriptions below and
must quote the exact provision text that grounds each code.

## Restrictiveness anchors (all domains)

| Score | Anchor |
|-------|--------|
| 0     | No restriction in this domain; the provision does not constrain the activity |
| 0.5   | Conditional restriction: licences, registrations, thresholds, adequacy tests, case-by-case approvals |
| 1.0   | Prohibition or near-total restriction of the activity |

Direction: "restrictive" (scores above 0), "permissive" (explicitly enables or
liberalizes the activity), "neutral" (mentions the activity without constraining
or enabling it).

Bindingness: "binding_law" (statutes, regulations, mandatory standards),
"soft_law" (codes of conduct, ethical guidelines with no legal force),
"guidance" (interpretive notices, FAQs, non-binding clarifications).

## Domain 1: data_governance

Cross-border transfer restrictions, data-localization mandates, consent and
data-access rules affecting AI training or deployment data.

- 0: no transfer/localization conditions
- 0.5: adequacy decisions, standard contractual clauses, licensing conditions
- 1.0: outright transfer prohibition or unconditional localization mandate

## Domain 2: risk_based_ai_regulation

Risk-tier definitions, conformity assessment, and obligations attached to
high-risk AI uses.

- 0: no risk-tier regime
- 0.5: risk classification with lighter duties for lower tiers
- 1.0: bans on specific uses or full pre-market assessment for broad categories

## Domain 3: compute_export_controls

Restrictions on chips, cloud computing capacity, or supercomputing, including
export, re-export, and use restrictions.

- 0: no compute restrictions
- 0.5: licensing requirements or threshold-based controls
- 1.0: export embargo or blanket prohibition

## Domain 4: model_algorithm_oversight

Transparency, auditing, registration, and content rules for AI models and
algorithms, including generative-AI obligations.

- 0: no oversight duties
- 0.5: disclosure, registration, or audit duties
- 1.0: mandatory pre-release approval or sweeping content prohibitions

## Domain 5: ai_talent_migration

Visas, occupational access, and talent programmes affecting the cross-border
mobility of AI-skilled workers.

- 0: no constraints on AI talent mobility
- 0.5: quotas, sponsorship, or occupation-list restrictions
- 1.0: effective closure to foreign AI workers

## Rules

1. A provision may touch several domains; code all that apply.
2. Codes without a verbatim quote are invalid (human coders must also fill the
   quote column).
3. When in doubt between two scores, choose the lower and flag for adjudication.
4. Never code text outside the provision.
