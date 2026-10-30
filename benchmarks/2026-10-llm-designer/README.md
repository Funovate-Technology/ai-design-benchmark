# 2026-10-llm-designer

Eight language models act as the designer in FontVibe's design pipeline: they read a brief,
propose three design directions, and write the instructions for the image model. The image model
is fixed (GPT Image 2.5 Sunburst, 2K, medium quality), so the only thing that changes is the
designer.

- **Article:** [GPT-6.1 Terra vs Claude & Gemini: Design Test](https://fontvibe.ai/blog/gpt-6-1-terra-vs-claude-gemini-design-test)
- **Date:** October 30, 2026, on FontVibe's production pipeline with an official account
- **Briefs:** 12, in four layers of three (everyday requests, getting the information right,
  design judgement, language and culture), in English, Chinese, Spanish, Portuguese, German and Japanese
- **Runs:** 3 per brief per model, 288 in all. 269 finished and are ranked. 19 failed because of
  the model's own output and were not rerun:
  - 17 Claude Opus 5.5 proposals cut off at the 6,600-token output limit
  - 1 Claude Opus 5.5 run whose image instructions were not valid JSON (b03-anthropic_opus55-r3)
  - 1 empty GPT-5.6 Terra proposal

  Opus proposals reached the 6,600-token limit in 19 runs; 2 of them still finished. One GPT-6 Luna
  proposal also reached it and finished.
- **Side note:** the 18 failed Opus runs again with both output limits doubled
  (`opus-budget-2x.jsonl`; all 18 finished). Not part of the ranking, because no other model got
  a larger limit.
- **Scoring:** [SCORING.md](../../SCORING.md) v1.2, by AI judges running Claude Opus 5.5 that saw
  anonymous IDs. Claude Opus 5.5 is also one of the tested models.

```bash
python3 ../../scripts/analyze.py .
```

## Files

| File | Contents |
|---|---|
| `briefs.json` | The 12 briefs, their layer and language. `must_appear` is the text that had to appear, in English; `must_appear_as_given_to_judge` is the same list as the judge received it (judging notes in Chinese) |
| `models.json` | Model IDs, provider, reasoning effort, public price on the test date with its source, and what each provider's token fields include |
| `designs.jsonl` | One line per run (288): status and failure cause, number of attempts, the three proposed directions, the image instructions, time, tokens, internal retries and cost of each step, the image, the four scores, the judge's text checks and reasons |
| `attempts.jsonl` | Every attempt (300): which one was used, and why earlier attempts were replaced |
| `opus-budget-2x.jsonl` | The 18 Claude Opus 5.5 side-note reruns |
| `blind-pick.json` | One person's anonymised pick per brief (a side note, not part of the ranking) |
| `summary.csv`, `pairs.csv` | Written by `analyze.py`: the per-model table and all 28 pairwise comparisons |

## How runs were handled

- Each run renders the **first** of the three proposed directions. Nothing was picked by hand.
- A run was rerun only when it never got a fair attempt: a provider error (rate limit, timeout;
  8 attempts, all Gemini 3.8 Flash) or FontVibe's front desk asking the user a question before
  the designer started (4 attempts: 2 GPT-5.6 Terra, 2 GPT-6.1 Sol). The rerun's result is the one
  used; `attempts.jsonl` lists every attempt. Failures of the model's own output were never rerun.
- `internal_retries` counts the pipeline's own retries inside one request, with the same model,
  after an attempt failed (for example a cut-off proposal tried once more).
- Costs use each provider's public price on October 30, 2026 (`models.json`). Token fields follow
  each provider's own accounting, which differs (see `token_fields`). `analyze.py` reports both the
  median cost of a finished design and the total spend, including failed runs and reruns, divided
  by finished designs.

## Statistics

- The three runs of a brief were scored by the same judge in the same pass, so they are not
  independent. Confidence intervals resample briefs, not single designs.
- Two models are compared on the briefs where both have finished designs, using the difference of
  their per-brief means and a bootstrap interval. An interval that crosses zero is reported as a
  tie. There are 28 pairs and no correction for multiple comparisons.
- Claude Opus 5.5 finished designs on only 8 of the 12 briefs (none on briefs 5, 8, 11 and 12),
  mostly easier ones. Its main-table mean is not directly comparable with the full-coverage models;
  `analyze.py` also compares it on the shared briefs and, as a side note, with all 36 designs.

## Limits

- One AI judge pass per brief, with no repeat scoring and no second judge. The judge model is also
  one of the tested models, and whether it favours its own designs was not tested.
- 12 briefs, 3 runs each; one image model; first direction only.
- The judge's reasons are in Chinese, as written. [SCORING.md](../../SCORING.md) is an English
  translation of the instructions the judge received; the original is [SCORING.zh.md](../../SCORING.zh.md).

## Blind pick (side note)

For each brief, one finished run per model was drawn at random (seed 20261031). Where Opus had no
finished run on a brief, one of its doubled-limit reruns was drawn instead. The eight designs were
shuffled and shown with no names. The person was FontVibe's founder, not the client for any brief.
Two of the 12 picks were the judges' top-scoring design among the eight shown; none was the
top-scoring design of the brief overall.

## Not published

FontVibe's production system prompts for the proposal and image-instruction steps, and the front
desk's prompt, are not part of this repository. Researchers who need them to reproduce the test
can ask at hello@fontvibe.ai.
