#!/usr/bin/env python3
"""
Recompute the published tables of the 2026-10-llm-designer benchmark from its raw data.

    python3 scripts/analyze.py benchmarks/2026-10-llm-designer

Prints, and writes next to the data:
  summary.csv  per model: finished runs, mean overall score with a 95% confidence interval,
               the four scores, text problems, cost, time and reliability
  pairs.csv    all pairwise comparisons between models (paired by brief)
and prints the Claude Opus 5.5 side note (doubled output limit).

Statistics:
  - The three runs of a brief share one brief and were scored by one judge in one pass, so they
    are not independent. Confidence intervals therefore resample briefs (cluster bootstrap),
    not single designs.
  - Two models are compared on the briefs where both have finished designs: the difference of
    their per-brief means, with a bootstrap interval over those briefs. If the interval crosses
    zero the two are called a tie. No correction for multiple comparisons is applied.
  - Fixed seed, so every run prints the same numbers.

Standard library only. Only this benchmark has an analysis script; the two image-model
benchmarks publish their per-image scores but no script.
"""
import csv, itertools, json, random, statistics, sys
from collections import defaultdict
from pathlib import Path

SEED = 20261030
N_BOOT = 4000
DIMS = ["legibility", "lettering_and_finish", "information_and_layout", "appeal"]


def load(path):
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def cluster_ci(groups):
    """95% bootstrap interval of the mean over designs, resampling whole briefs."""
    rng = random.Random(SEED)
    keys = list(groups)
    means = []
    for _ in range(N_BOOT):
        pick = [v for k in rng.choices(keys, k=len(keys)) for v in groups[k]]
        means.append(statistics.mean(pick))
    means.sort()
    return means[int(0.025 * N_BOOT)], means[int(0.975 * N_BOOT)]


def mean_ci(values):
    """95% bootstrap interval of a plain mean (used for per-brief differences)."""
    rng = random.Random(SEED)
    means = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(N_BOOT))
    return means[int(0.025 * N_BOOT)], means[int(0.975 * N_BOOT)]


def p90(values):
    return statistics.quantiles(values, n=10, method="inclusive")[-1]


def step_cost(d, step):
    u = (d.get(step) or {}).get("usage")
    return (u or {}).get("cost_usd") or 0.0


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "benchmarks/2026-10-llm-designer")
    designs = load(root / "designs.jsonl")
    attempts = load(root / "attempts.jsonl")
    side = load(root / "opus-budget-2x.jsonl")
    names = {m["model"]: m["name"] for m in json.load(open(root / "models.json"))}

    by = defaultdict(list)
    for d in designs:
        by[d["model"]].append(d)
    tries = defaultdict(list)
    for a in attempts:
        tries[a["model"]].append(a)

    # Per model, per brief, the overall scores of finished designs.
    per_brief = {m: defaultdict(list) for m in by}
    for d in designs:
        if d["status"] == "finished":
            per_brief[d["model"]][d["brief"]].append(d["scores"]["overall"])

    rows = []
    for model, ds in by.items():
        done = [d for d in ds if d["status"] == "finished"]
        overall = [d["scores"]["overall"] for d in done]
        lo, hi = cluster_ci(per_brief[model])
        cost_done = [step_cost(d, "proposal") + step_cost(d, "image_instructions") for d in done]
        # Every attempt costs money, including failed runs and reruns (attempts.jsonl).
        at = tries[model]
        spend = sum(a["cost_usd"] for a in at)
        rows.append({
            "model": model, "name": names[model], "runs": len(ds), "finished": len(done),
            "briefs_covered": len(per_brief[model]),
            "overall": round(statistics.mean(overall), 2), "ci_low": round(lo, 2), "ci_high": round(hi, 2),
            **{dim: round(statistics.mean(d["scores"][dim] for d in done), 1) for dim in DIMS},
            "invented_lines_per_design": round(statistics.mean(len(d["judge"]["text_invented"]) for d in done), 2),
            "share_not_fully_fitting_intent": round(statistics.mean(d["judge"]["intent_fit"] != "fits" for d in done), 2),
            "median_cost_usd": round(statistics.median(cost_done), 4),
            "spend_per_finished_design_usd": round(spend / len(done), 4),
            "median_proposal_seconds": round(statistics.median(d["proposal"]["usage"]["seconds"] for d in done), 1),
            "p90_proposal_seconds": round(p90([d["proposal"]["usage"]["seconds"] for d in done]), 1),
            "median_image_instructions_seconds": round(statistics.median(d["image_instructions"]["usage"]["seconds"] for d in done), 1),
            "p90_image_instructions_seconds": round(p90([d["image_instructions"]["usage"]["seconds"] for d in done]), 1),
            "first_attempt_finished": sum(1 for a in at if a["attempt"] == 1 and a["status"] == "finished"),
            "model_failures": sum(1 for a in at if a["cause"] == "model"),
            "provider_errors": sum(1 for a in at if a["cause"] == "provider"),
            "front_desk_reruns": sum(1 for a in at if a["cause"] == "front_desk"),
            "internal_retries": sum(a["internal_retries"] for a in at),
        })
    rows.sort(key=lambda r: -r["overall"])
    for r in rows:
        print(f"{r['name']:<18} {r['overall']:.2f} [{r['ci_low']:.2f}, {r['ci_high']:.2f}]  "
              f"finished {r['finished']}/{r['runs']} on {r['briefs_covered']} briefs  "
              f"invented {r['invented_lines_per_design']:.2f}/design  median ${r['median_cost_usd']:.4f}  "
              f"spend/finished ${r['spend_per_finished_design_usd']:.4f}  "
              f"{r['median_proposal_seconds']} s + {r['median_image_instructions_seconds']} s  "
              f"first try {r['first_attempt_finished']}/{r['runs']}  provider errors {r['provider_errors']}  "
              f"internal retries {r['internal_retries']}")
    with open(root / "summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    # All pairwise comparisons, paired by brief.
    order = [r["model"] for r in rows]
    pairs = []
    print("\nPairwise, paired by brief (difference of per-brief means, 95% interval):")
    for a, b in itertools.combinations(order, 2):
        common = sorted(set(per_brief[a]) & set(per_brief[b]))
        diffs = [statistics.mean(per_brief[a][k]) - statistics.mean(per_brief[b][k]) for k in common]
        lo, hi = mean_ci(diffs)
        verdict = "tie" if lo <= 0 <= hi else (f"{names[a]} higher" if lo > 0 else f"{names[b]} higher")
        pairs.append({"model_a": a, "model_b": b, "briefs": len(common), "difference": round(statistics.mean(diffs), 2),
                      "ci_low": round(lo, 2), "ci_high": round(hi, 2), "verdict": verdict})
        print(f"  {names[a]:<18} − {names[b]:<18} {len(common):2d} briefs  {statistics.mean(diffs):+.2f} [{lo:+.2f}, {hi:+.2f}]  {verdict}")
    with open(root / "pairs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(pairs[0]))
        w.writeheader()
        w.writerows(pairs)

    # The comparison the test started from, score by score.
    a, b = "gpt-6.1-terra", "gpt-5.6-terra"
    if a in by and b in by:
        common = sorted(set(per_brief[a]) & set(per_brief[b]))
        print(f"\n{names[a]} − {names[b]}, paired by brief ({len(common)} briefs):")
        for dim in DIMS + ["overall"]:
            pb = {m: defaultdict(list) for m in (a, b)}
            for d in by[a] + by[b]:
                if d["status"] == "finished":
                    pb[d["model"]][d["brief"]].append(d["scores"][dim])
            diffs = [statistics.mean(pb[a][k]) - statistics.mean(pb[b][k]) for k in common]
            lo, hi = mean_ci(diffs)
            print(f"  {dim:<24} {statistics.mean(diffs):+.2f} [{lo:+.2f}, {hi:+.2f}]  lower on {sum(x < 0 for x in diffs)} of {len(diffs)} briefs")

    # Side note: Claude Opus 5.5 with the output limit doubled, rerun on its 18 failed runs.
    opus = "claude-opus-5-5"
    if side and opus in by:
        s_done = [d for d in side if d["status"] == "finished"]
        print(f"\nSide note: {names[opus]} with doubled output limit: {len(s_done)}/{len(side)} finished, "
              f"mean {statistics.mean(d['scores']['overall'] for d in s_done):.2f}")
        full = defaultdict(list)
        for k, v in per_brief[opus].items():
            full[k] += v
        for d in s_done:
            full[d["brief"]].append(d["scores"]["overall"])
        vals = [v for vs in full.values() for v in vs]
        lo, hi = cluster_ci(full)
        print(f"  all {len(vals)} designs: {statistics.mean(vals):.2f} [{lo:.2f}, {hi:.2f}]")
        for b in order:
            if b == opus:
                continue
            common = sorted(set(full) & set(per_brief[b]))
            diffs = [statistics.mean(full[k]) - statistics.mean(per_brief[b][k]) for k in common]
            lo, hi = mean_ci(diffs)
            print(f"  vs {names[b]:<18} {statistics.mean(diffs):+.2f} [{lo:+.2f}, {hi:+.2f}]  "
                  f"{'tie' if lo <= 0 <= hi else 'separated'}")


if __name__ == "__main__":
    main()
