# Evaluation dataset

`basic-dataset.json` contains the lesson's two initial behavioral cases:

1. A complete qualified-client intake that must traverse the valid graph.
2. An incomplete intake that must terminate on the correction branch.

Generate and grade the final traces with:

```bash
agents-cli eval generate --output artifacts/traces/final.json
agents-cli eval grade \
  --traces artifacts/traces/final.json \
  --config tests/eval/eval_config.yaml \
  --output artifacts/grade_results/final_domain
```

The configuration combines a deterministic route metric, a graph-aware local
Gemini judge, and deterministic onboarding safety checks.
