# Few-shot examples (v1, ILLUSTRATIVE)

The provisions below are FICTIONAL and serve only as format examples. Replace
with real annotated examples drawn from the adjudicated gold standard.

## Example 1

Provision: "A controller may transfer personal data used for training AI systems
to a third country only where that country ensures an adequate level of
protection, as determined by the Data Authority."

Expected output:

    {
      "applies": true,
      "domains": ["data_governance"],
      "direction": "restrictive",
      "restrictiveness": 0.5,
      "bindingness": "binding_law",
      "scope": "controllers transferring AI training data to third countries",
      "quote": "may transfer personal data used for training AI systems to a third country only where that country ensures an adequate level of protection"
    }

## Example 2

Provision: "The export of advanced AI accelerators to entities outside Atlantis
requires a licence from the Export Control Office."

Expected output:

    {
      "applies": true,
      "domains": ["compute_export_controls"],
      "direction": "restrictive",
      "restrictiveness": 0.5,
      "bindingness": "binding_law",
      "scope": "exporters of advanced AI accelerators",
      "quote": "The export of advanced AI accelerators to entities outside Atlantis requires a licence"
    }
