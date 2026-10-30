#!/usr/bin/env python3
"""
Recompute the published tables from the raw data of one benchmark.

    python3 scripts/analyze.py benchmarks/2026-10-llm-designer

Prints the ranking (mean overall score with a 95% bootstrap confidence interval,
the four scores, invented lines per design, finish rate, cost and time) and the
paired comparison between two models, and writes summary.csv next to the data.
Standard library only.
"""
import csv, json, random, statistics, sys
from collections import defaultdict
from pathlib import Path

SEED = 20261030
DIMS = ["legibility", "lettering_and_finish", "information_and_layout", "appeal"]


def load(path):
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def ci(values, n=4000):
    """95% bootstrap confidence interval of the mean (fixed seed, so the output is reproducible)."""
    rng = random.Random(SEED)
    means = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n)]


def pct(values, q):
    values = sorted(values)
    return values[min(len(values) - 1, int(round(q * (len(values) - 1))))] if values else None


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "benchmarks/2026-10-llm-designer")
    designs = load(root / "designs.jsonl")
    names = {m["model"]: m["name"] for m in json.load(open(root / "models.json"))}
    by = defaultdict(list)
    for d in designs:
        by[d["model"]].append(d)

    rows = []
    for model, ds in by.items():
        done = [d for d in ds if d["status"] == "finished"]
        overall = [d["scores"]["overall"] for d in done]
        lo, hi = ci(overall)
        cost = [d["proposal"]["usage"]["cost_usd"] + d["image_instructions"]["usage"]["cost_usd"] for d in done]
        rows.append({
            "model": model, "name": names[model], "finished": len(done), "runs": len(ds),
            "overall": round(statistics.mean(overall), 2), "ci_low": round(lo, 2), "ci_high": round(hi, 2),
            **{dim: round(statistics.mean(d["scores"][dim] for d in done), 1) for dim in DIMS},
            "invented_lines_per_design": round(statistics.mean(len(d["judge"]["text_invented"]) for d in done), 2),
            "partly_fits_intent": sum(d["judge"]["intent_fit"] != "fits" for d in done),
            "median_cost_usd": round(statistics.median(cost), 4),
            "median_proposal_seconds": pct([d["proposal"]["usage"]["seconds"] for d in ds if d["proposal"]["usage"]], 0.5),
        })
    rows.sort(key=lambda r: -r["overall"])
    for i, r in enumerate(rows, 1):
        print(f"{i}. {r['name']:<18} {r['overall']:.2f} [{r['ci_low']:.2f}, {r['ci_high']:.2f}]  "
              f"finished {r['finished']}/{r['runs']}  invented {r['invented_lines_per_design']:.2f}/design  "
              f"${r['median_cost_usd']:.4f}  {r['median_proposal_seconds']} s")
    with open(root / "summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    # Paired comparison: same brief, same run number, both finished.
    a, b = "gpt-6.1-terra", "gpt-5.6-terra"
    if a in by and b in by:
        key = lambda d: (d["brief"], d["run"])
        da = {key(d): d for d in by[a] if d["status"] == "finished"}
        db = {key(d): d for d in by[b] if d["status"] == "finished"}
        diffs = [da[k]["scores"]["overall"] - db[k]["scores"]["overall"] for k in da if k in db]
        lo, hi = ci(diffs)
        print(f"\n{names[a]} − {names[b]}, paired (n={len(diffs)}): {statistics.mean(diffs):+.2f} [{lo:+.2f}, {hi:+.2f}], "
              f"{sum(x > 0 for x in diffs)} wins / {sum(x < 0 for x in diffs)} losses")


if __name__ == "__main__":
    main()
