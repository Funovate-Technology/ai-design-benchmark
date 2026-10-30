# 2026-10-llm-designer

Eight language models act as the designer in FontVibe's design pipeline: they read a brief,
propose three design directions, and write the instructions for the image model. The image model
is fixed (GPT Image 2.5 Sunburst, 2K, medium quality), so the only thing that changes is the
designer.

- **Article:** [GPT-6.1 Terra vs Claude & Gemini: Design Test](https://fontvibe.ai/blog/gpt-6-1-terra-vs-claude-gemini-design-test)
- **Date:** October 30, 2026, on FontVibe's production pipeline with an official account
- **Briefs:** 12, in four layers of three (everyday requests, getting the information right,
  design judgement, language and culture), in English, Chinese, Spanish, Portuguese, German and Japanese
- **Runs:** 3 per brief per model, 288 in all; 269 finished, 19 failed because of the model's own
  output (18 Claude Opus 5.5 proposals cut off at the 6,600-token limit, 1 empty GPT-5.6 Terra proposal)
- **Side note:** the 18 Opus runs again with both output limits doubled (`opus-budget-2x.jsonl`)
- **Scoring:** [SCORING.md](../../SCORING.md) v1.2, by AI judges running Claude Opus 5.5 that saw
  anonymous IDs. Claude Opus 5.5 is also one of the tested models.

```bash
python3 ../../scripts/analyze.py .
```
