# Scoring standard

Version 1.2, October 30, 2026. This is the standard used for `2026-10-llm-designer`. The two
earlier image-model benchmarks used its predecessor (the same four scores and weights; see the
note at the end).

## Scope

The standard covers **designs with text**. Lettering and finish carries the largest weight, so it
measures how well a model designs with type. Images without text (pure illustration, photos) are
out of scope.

## How a benchmark is run

- Every brief asks for text on the design, and lists the text that must appear. That list is the
  only reference for judging text accuracy.
- Only the part being tested changes. Everything else (image model, prompts, output format,
  reasoning effort, limits) is the same for every model. A model is never given its own settings.
  If a limit has to be raised to see what a model can do, that is run as a separate side note and
  kept out of the main ranking.
- At least three runs per brief per model. The first result is the one rendered and scored; nothing
  is picked by hand.
- Failures are classified from logs: the model's own output (cut off at the limit, empty or broken)
  counts as a failure and is not rerun; provider errors and pipeline steps that are not under test
  are rerun and reported separately.
- The main ranking comes from the scores below. Judges see anonymous IDs, never model names. All
  designs for one brief are scored by the same judge in one pass. A person picking by first
  impression is reported only as a side note, with who they are.
- Results report the mean with a 95% bootstrap confidence interval, the four scores, per-layer
  scores and text problems per design. Two models are compared with a paired difference (same
  brief, same run) and its interval; if the interval crosses zero, they are called a tie.

## The judge's instructions

### Your position

You are the client who commissioned this design. You wrote the brief and you will use the design.
You decide three things: **is it what I asked for; can I use it without it going wrong; does it
make me say "wow" at first sight, and would I actually use it.**

The design is anonymous. Do not guess which model made it, and do not let "this style is common"
affect your judgement.

### Order of judgement

Judge in this order. A problem higher up cannot be made up for lower down.

1. **Is it the right deliverable?** Is it the thing the brief asked for, and can it be used as that
   thing? A beautiful design of the wrong thing cannot be used.
2. **Is the information right?** The information in the brief must be complete, accurate and in the
   client's own wording, and every piece of text on the design must be something the client can
   stand behind. Ask: *would I have to change this before using it, and did I ever say it — is it
   true?* A faithful restatement of what the brief says, or a necessary functional label, is
   something the client accepts. Facts, figures, promises and slogans the client never gave and
   cannot check are errors: the client must either delete them or publish something untrue without
   noticing. Placeholders printed as is, and changes to how the client wrote something, are errors
   too.
3. **Is it the feeling the client wanted?** The intent the brief states or reasonably implies: who
   it is for, where it will be used, the mood it should have, what to avoid. The designer may take
   its own direction, but the direction serves the brief; where they disagree, the brief wins.
4. **Are the details well made?** Letterforms, materials, textures, lines, colour, light: do they
   achieve the intended effect, and are they refined, believable and good up close?
5. **First impression.** Does it make you say "wow", does it look like a professional designer's
   work, is there something memorable, and would you actually use it?

### The four scores (1–10 each; write the reason before the number)

Each score covers its own question. A problem is deducted once, under the score it belongs to,
never again under another. Missing, changed or invented text all belong to information and layout.

- **Legibility (20%).** First look for hard errors: anything that would make the main message
  misread or unreadable at its real size. Any hard error: 1–4. None: 7–10, by how easily the main
  message reads. Problems with secondary text go under information and layout. Text that is too
  small to read at the image's own resolution is not a hard error.
- **Lettering and finish (35%).** How well the letterforms and materials achieve the effect and mood
  the brief wants (points 3 and 4). Where the brief sets no effect, whether the chosen effect fits the
  brief's intent and how well it is made. Lettering and materials only; layout problems do not
  belong here.
- **Information and layout (25%).** First points 1 and 2: the wrong deliverable costs 3 points; each
  missing, changed or unsupported piece of text costs at least 1 point, with the text quoted in the
  reason. Then whether the most important information reads first, whether order and grouping make
  sense, and finally balance, white space and polish.
- **Appeal (20%).** First impression and visual professionalism only: would a client who wanted this
  be won over at first sight, and does it look like a professional designer's work? Fitting the
  brief's intent (point 3) comes first; looking good while going against the intent earns nothing.
  Text accuracy is judged under information and layout and is not deducted again here.

| Score | Legibility | Lettering and finish | Information and layout | Appeal |
|---|---|---|---|---|
| 9–10 | No hard error; reads at a glance even as a thumbnail | Every intended effect achieved and refined; matches the brief's intent closely | Complete and accurate, hierarchy obvious at once, careful layout | "Wow" at first sight; professional, memorable, exactly the feeling the client wanted |
| 7–8 | No hard error; takes a moment to read | Mostly achieved, flaws in the details, or broadly matches the intent | Complete and accurate, clear hierarchy, ordinary layout | Looks professional but generic |
| 5–6 | (not used) | Half achieved, ordinary finish, or clearly off the intent | One information problem, or unclear hierarchy | Amateur, or the wrong feeling |
| 1–4 | Has a hard error | Not achieved, cheap, distorted, or the opposite of the intent | Key information missing or wrong, several pieces of text the client could not stand behind, or unbalanced | Not usable |

### Keeping one scale

- Look at every design for a brief before scoring any of them. Clearly better and clearly worse
  designs in the same brief should be scored clearly apart.
- Look at every original image, not thumbnails.
- When already-scored anchor designs are provided, look at them first and keep to their scale.

### Output per design (fields in the order of judgement)

`id`, `deliverable_ok` (with a note), `missing` / `altered` / `invented` / `placeholders_printed`
(each quoted), `intent_fit` (fits / partly fits / does not fit, with one line of reason),
`legibility {hard_defects, reason, score}`, `lettering_and_finish {reason, score}`,
`information_and_layout {reason, score}`, `appeal {reason, score}`, `notes`. No overall score: it is
calculated.

```
overall = 0.20 × legibility + 0.35 × lettering and finish + 0.25 × information and layout + 0.20 × appeal
```

## Earlier versions

The 2026-10 image-model benchmarks (Grok Imagine 2.0, Qwen Image 3.0) used the same four scores,
weights and formula, with the prompt's lettering effect as the target for lettering and finish,
text checked line by line against the prompt, and a 3-point deduction for the wrong deliverable.
Version 1.2 adds the client's stance and priority order, judges intent (mood, audience, use) where
the brief describes a feeling rather than an effect, and keeps text problems out of appeal.
