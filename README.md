# AI Design Benchmark

**Open data from FontVibe's tests of AI models doing design work with text: logos, posters,
signs, invitations, thumbnails and packaging.** Every brief, every output, every image, every
score and the written reason behind each score.

Each benchmark asks one question: a client hands over a brief; can they use what the model
delivers, and are they happy with it? The full write-up of each test is on the
[FontVibe blog](https://fontvibe.ai/blog); this repository is the raw material behind it.

<!-- counts:start -->
```
  3   benchmarks
  8   language models tested as designers   (2026-10-llm-designer)
  5   image models at 8 settings tested      (2026-10-grok-imagine-2, 2026-10-qwen-image-3)
  494 images; every scored one has four scores and a written reason
```
<!-- counts:end -->

## The benchmarks

| Benchmark | What it tests | Article | Data |
|---|---|---|---|
| **2026-10-llm-designer** | 8 language models (GPT-6.1 Terra, GPT-5.6 Terra, GPT-6.1 Sol, GPT-6 Luna, Claude Opus 5.5, Claude Sonnet 5.5, Gemini 4 Argon, Gemini 3.8 Flash) acting as the designer: reading a brief, proposing directions and writing the image instructions. The image model is fixed. 12 briefs × 3 runs: 288 runs, 269 designs ranked, plus 18 side-note reruns. | [GPT-6.1 Terra vs Claude & Gemini: Design Test](https://fontvibe.ai/blog/gpt-6-1-terra-vs-claude-gemini-design-test) | [benchmarks/2026-10-llm-designer](benchmarks/2026-10-llm-designer) |
| **2026-10-qwen-image-3** | 5 image models on 10 design jobs with text: Qwen Image 3.0 Pro, GPT Image 2.5 Sunburst, Nano Banana 2.1, Seedream 5.0 Pro, Grok Imagine 2.0 | [Qwen Image 3.0 vs GPT Image, Nano Banana, Seedream & Grok](https://fontvibe.ai/blog/qwen-image-3-text-test) | [benchmarks/2026-10-qwen-image-3](benchmarks/2026-10-qwen-image-3) |
| **2026-10-grok-imagine-2** | 4 image models (Grok Imagine 2.0 at Low and Medium, GPT Image 2.5 Sunburst, Nano Banana 2.1, Seedream 5.0 Pro) on 10 design jobs with text | [Grok Imagine 2.0 text test](https://fontvibe.ai/blog/grok-imagine-2-text-test) | [benchmarks/2026-10-grok-imagine-2](benchmarks/2026-10-grok-imagine-2) |

## How designs are scored

Every design gets four scores from 1 to 10. The overall score is calculated, not judged:

```
overall = 0.20 × legibility + 0.35 × lettering and finish + 0.25 × information and layout + 0.20 × appeal
```

The judge plays the client who wrote the brief: is it the thing I asked for; can I use every piece
of text as it is; does it have the feeling I wanted; are the details well made; does it impress at
first sight. Text the client never gave (founding years, slogans, figures) and placeholders printed
as is count against a design. The full standard is in [SCORING.md](SCORING.md). It covers designs
with text; images without text are out of scope.

## Reproduce the numbers

```bash
python3 scripts/analyze.py benchmarks/2026-10-llm-designer
python3 scripts/verify.py
```

Standard library only. `analyze.py` recomputes the tables of the llm-designer benchmark: the
per-model table with 95% bootstrap confidence intervals (resampling briefs, fixed seed), cost,
time and reliability, and all pairwise comparisons; it writes `summary.csv` and `pairs.csv`. The
two image-model benchmarks publish every score but have no analysis script. `verify.py` checks
counts, score arithmetic, attempts and that every image URL resolves.

## What's in a benchmark folder

`2026-10-llm-designer/`

| File | Contents |
|---|---|
| `briefs.json` | The 12 briefs, their layer, language and the text that must appear |
| `models.json` | Model IDs, providers, reasoning effort and public prices on the test date |
| `designs.jsonl` | One line per run (288): status and failure cause, the three proposed directions, the image instructions, time, tokens, retries and cost of each step, the image, the four scores, the judge's text checks and reasons |
| `attempts.jsonl` | Every attempt (300), with the cause of each replaced attempt |
| `opus-budget-2x.jsonl` | 18 reruns of Claude Opus 5.5 with the output limit doubled (a side note, not in the ranking) |
| `blind-pick.json` | One person's anonymised pick per brief (a side note, not in the ranking) |
| `summary.csv`, `pairs.csv` | Per-model table and all pairwise comparisons, written by `analyze.py` |

The image-model folders hold `tasks.json` (prompts and required text) and `images.jsonl` (every
image generated, which ones were scored, the scores and reasons).

Judges' reasons are in Chinese (`reasons_zh`, `reason_zh`), as written at scoring time; the judge's
instructions were in Chinese too ([SCORING.zh.md](SCORING.zh.md)). The benchmark folder's README
lists how runs were handled, the statistics and the limits.

In the two image-model folders, `"scored": false` images were extra samples used for consistency
checks, and `designer-grok2-low` images went through FontVibe's designer mode (shown in the
article, not scored). Four generations in `2026-10-qwen-image-3` failed (one Nano Banana 2.1, three
Seedream 5.0 Pro); their causes were not recorded. Each task and setup has one scored image, so
those tables have no confidence intervals.

## Images

Images are hotlinked from `cos.fontvibe.ai/opensource/ai-design-benchmark/…`. Each record also
links the design's page on FontVibe (`fontvibe_page`), where it can be viewed full size and
remade. Images are not part of this repository and remain subject to
[FontVibe's terms](https://fontvibe.ai/terms).

## Attribution

The data is [CC BY 4.0](LICENSE); the scripts are [MIT](LICENSE-CODE). If you publish results,
charts or examples from this data, please credit it like this, linking the article of the
benchmark you used:

**Markdown**
```markdown
Data: [FontVibe AI Design Benchmark](https://fontvibe.ai/blog/gpt-6-1-terra-vs-claude-gemini-design-test) ·
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
```

**HTML**
```html
Data: <a href="https://fontvibe.ai/blog/gpt-6-1-terra-vs-claude-gemini-design-test">FontVibe AI Design Benchmark</a> ·
<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>
```

**Plain text**
```
Data: FontVibe AI Design Benchmark — https://fontvibe.ai/blog/gpt-6-1-terra-vs-claude-gemini-design-test — CC BY 4.0
```

- **Please link the article, not just this repo.** The article shows the designs side by side and
  explains the method; that is what your readers will want.
- **`rel="nofollow"` is fine.** We would rather be credited with a nofollow link than not at all.
- **A link is not strictly required** where it isn't practical, such as in print.

## Citing it

See [CITATION.cff](CITATION.cff). GitHub shows a "Cite this repository" button for it.

## Who made this

[FontVibe](https://fontvibe.ai) is an AI design tool for text effects and lettering, made by
Funovate Technology. FontVibe uses some of the models tested here in production, and the
llm-designer benchmark ran through FontVibe's own pipeline; both are stated in the articles.
FontVibe's production system prompts are not published; researchers who need them can ask at
hello@fontvibe.ai. Corrections and reruns are welcome: open an issue or email hello@fontvibe.ai.

## Changes

- **1.0.1** (2026-10-31): corrected the causes of the 19 failed llm-designer runs (17 cut off at
  the limit, 1 invalid image instructions, 1 empty); added `attempts.jsonl` (every attempt, with
  provider errors, front-desk reruns, internal retries and cost); confidence intervals now resample
  briefs, and all 28 pairwise comparisons are published (`pairs.csv`); cost now also reported as
  total spend per finished design; price sources and token-field notes in `models.json`;
  `must_appear` in English; the judge's original Chinese instructions (`SCORING.zh.md`).
- **1.0.0** (2026-10-30): first release.
