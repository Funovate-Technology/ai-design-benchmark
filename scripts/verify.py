#!/usr/bin/env python3
"""
Check the data: record counts, score arithmetic, required fields, and (unless --offline)
that every image URL answers 200.

    python3 scripts/verify.py [--offline]
"""
import json, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "benchmarks"
W = (0.20, 0.35, 0.25, 0.20)
DIMS = ("legibility", "lettering_and_finish", "information_and_layout", "appeal")
errors = []


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def check_scores(where, s):
    for d in DIMS:
        if not (isinstance(s[d], int) and 1 <= s[d] <= 10):
            errors.append(f"{where}: {d}={s[d]} out of 1–10")
    calc = round(sum(w * s[d] for w, d in zip(W, DIMS)), 2)
    if abs(calc - s["overall"]) > 0.006:
        errors.append(f"{where}: overall {s['overall']} != {calc}")


def main():
    urls = []
    llm = ROOT / "2026-10-llm-designer"
    designs = load(llm / "designs.jsonl")
    side = load(llm / "opus-budget-2x.jsonl")
    briefs = json.load(open(llm / "briefs.json", encoding="utf-8"))
    models = {m["model"] for m in json.load(open(llm / "models.json"))}
    if len(designs) != len(briefs) * len(models) * 3:
        errors.append(f"llm-designer: {len(designs)} runs, expected {len(briefs) * len(models) * 3}")
    for d in designs + side:
        if d["model"] not in models:
            errors.append(f"{d['id']}: unknown model {d['model']}")
        if d["status"] == "finished":
            check_scores(d["id"], d["scores"])
            urls.append(d["image"]["url"])
            if (d["judge"]["hard_defects"] != []) != (d["scores"]["legibility"] <= 4):
                errors.append(f"{d['id']}: hard defects and legibility band disagree")
        elif not d.get("failure"):
            errors.append(f"{d['id']}: failed without a cause")
    finished = sum(d["status"] == "finished" for d in designs) + len(side)
    print(f"llm-designer: {len(designs)} runs, {finished} scored designs (incl. {len(side)} budget-2x reruns)")
    for name in ("2026-10-grok-imagine-2", "2026-10-qwen-image-3"):
        imgs = load(ROOT / name / "images.jsonl")
        scored = [i for i in imgs if i.get("scored")]
        for i in scored:
            check_scores(f"{name} t{i['task']} {i['setup']}", i["scores"])
        urls += [i["image"] for i in imgs if i["status"] == "finished"]
        print(f"{name}: {len(imgs)} images, {len(scored)} scored")
    if "--offline" not in sys.argv:
        def status(u):
            try:
                req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "Mozilla/5.0 ai-design-benchmark-verify"})
                return u, urllib.request.urlopen(req, timeout=30).status
            except Exception as e:  # noqa: BLE001 report every failure
                return u, str(e)
        with ThreadPoolExecutor(16) as ex:
            for u, st in ex.map(status, urls):
                if st != 200:
                    errors.append(f"image {u}: {st}")
        print(f"checked {len(urls)} image URLs")
    for e in errors:
        print("ERROR", e)
    print("OK" if not errors else f"{len(errors)} error(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
