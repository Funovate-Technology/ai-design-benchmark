# 2026-10-grok-imagine-2

Image models on ten design jobs that all have text in them, each given the identical prompt.
The first image that finished for each job and setup was scored (`"scored": true` in
`images.jsonl`); the others were used for consistency checks.

- **Article:** <https://fontvibe.ai/blog/grok-imagine-2-text-test>
- **Files:** `tasks.json` (prompts, aspect ratios and required text), `images.jsonl` (every image
  generated, with its FontVibe page, time, and, for scored images, the four scores and the reason)
- **Scoring:** the predecessor of [SCORING.md](../../SCORING.md) (same four scores, weights and formula; see "Earlier versions")
