#!/usr/bin/env python3
"""Choose a least-cost capable model from an explicit JSON catalogue."""
import argparse
import json
import math
from pathlib import Path


def select(catalogue):
    if not isinstance(catalogue, dict):
        raise ValueError("catalogue root must be a JSON object")
    required = catalogue.get("required_capabilities")
    models = catalogue.get("models")
    if not isinstance(required, list) or not all(isinstance(x, str) for x in required):
        raise ValueError("required_capabilities must be a list of strings")
    if not isinstance(models, list):
        raise ValueError("models must be a list")
    if any(not isinstance(m, dict) for m in models):
        raise ValueError("each models entry must be an object")
    if any(not isinstance(m.get("id"), str) or not m["id"].strip() for m in models):
        raise ValueError("each model must have a non-empty string id")
    ids = [m["id"] for m in models]
    if len(set(ids)) != len(ids):
        raise ValueError("model ids must be unique")

    exclusions, unresolved, capable = [], [], []
    for m in models:
        reasons = []
        questions = []
        if m.get("available") is False:
            reasons.append("unavailable")
        elif m.get("available") is not True:
            questions.append("availability unknown")
        if m.get("authorized") is False:
            reasons.append("unauthorized")
        elif m.get("authorized") is not True:
            questions.append("authorization unknown")

        caps = m.get("capabilities")
        complete = m.get("capabilities_complete")
        if caps is not None and (not isinstance(caps, list)
                                 or not all(isinstance(c, str) for c in caps)):
            raise ValueError("capabilities must be null or a list of strings")
        if complete is not True:
            questions.append("capability list not confirmed complete")
        elif caps is None:
            questions.append("capabilities unknown")
        elif not set(required).issubset(set(caps)):
            reasons.append("required capability absent from complete list")

        if reasons:
            exclusions.append({"id": m["id"], "reasons": reasons})
        if questions:
            unresolved.append({"id": m["id"], "questions": questions})
        if reasons or questions:
            continue
        capable.append(m)

    if not capable:
        return {"status": "needs_information" if unresolved else "no_candidate_in_catalogue",
                "selected": None,
                "reason": ("No eligible capable model is established in the supplied catalogue; "
                           "this does not prove none exists outside it."),
                "unresolved": unresolved, "excluded": exclusions}

    def comparable_cost(m):
        cost = m.get("cost")
        if not isinstance(cost, dict):
            return False
        fields = ("metric", "unit", "workload", "window", "source", "as_of", "relative_rank")
        if not all(field in cost for field in fields):
            return False
        return (all(isinstance(cost[field], str) and cost[field].strip()
                    for field in fields[:-1])
                and isinstance(cost["relative_rank"], (int, float))
                and not isinstance(cost["relative_rank"], bool)
                and math.isfinite(cost["relative_rank"]))

    missing = [m["id"] for m in capable if not comparable_cost(m)]
    if missing:
        return {"status": "needs_information", "selected": None,
                "reason": ("Cost evidence must declare metric, unit, workload, window, source, "
                           "as_of, and a finite relative_rank."),
                "missing_cost": missing, "unresolved": unresolved, "excluded": exclusions}

    signatures = {(m["cost"]["metric"], m["cost"]["unit"],
                   m["cost"]["workload"], m["cost"]["window"],
                   m["cost"]["source"], m["cost"]["as_of"]) for m in capable}
    if len(signatures) != 1:
        return {"status": "needs_information", "selected": None,
                "reason": ("Capable candidates have different cost metrics, units, workloads, "
                           "windows, sources, or as_of dates."),
                "unresolved": unresolved, "excluded": exclusions}
    winner = min(capable, key=lambda m: m["cost"]["relative_rank"])
    return {"status": "selected", "selected": winner["id"],
            "comparison": {key: winner["cost"][key] for key in
                           ("metric", "unit", "workload", "window", "source", "as_of")},
            "supplied_relative_rank": winner["cost"]["relative_rank"],
            "reason": ("Lowest supplied rank for the declared matching cost comparison; "
                       "this is not a claim of real-world savings or a dispatch guarantee."),
            "unresolved": unresolved, "excluded": exclusions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalogue", type=Path, help="Path to a JSON catalogue")
    args = parser.parse_args()
    try:
        result = select(json.loads(args.catalogue.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
