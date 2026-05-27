"""Grader for the contable-experto eval.

Compares each model response against the expected output in the dataset.

Validations:
- If a brake is expected: empty lineas + flag freno_nominas = true
- Entry balance: |Σdebe - Σhaber| < 0.01
- For each expected line: find a matching actual line by PGC prefix + amount
  on the correct side (debit/credit), tolerance ±€0.01
- Semantic flags: exact match

Usage:
    python grader.py                               (list available results)
    python grader.py results/2026-05-27_1200.json  (grade a result file)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict


TOLERANCIA = 0.01


def grade_caso(expected: dict, actual: dict) -> dict:
    """Returns dict with score (0-1), issues list, pass bool."""
    issues = []

    if "_parse_error" in actual:
        return {
            "pass": False,
            "score": 0.0,
            "issues": [f"JSON parsing failed: {actual.get('_parse_error', '?')}"],
        }

    # 1. Estado
    expected_estado = expected.get("estado", "OK")
    actual_estado = actual.get("estado", "OK")
    if expected_estado != actual_estado:
        issues.append(f"Estado: expected {expected_estado}, received {actual_estado}")

    # 2. Brake case: empty lineas + flag active
    expected_freno = expected.get("flags", {}).get("freno_nominas", False)
    if expected_freno:
        actual_lineas = actual.get("lineas", [])
        if len(actual_lineas) > 0:
            issues.append(f"Expected brake (0 lines), received {len(actual_lineas)} lines")
        actual_freno = actual.get("flags", {}).get("freno_nominas", False)
        if not actual_freno:
            issues.append("Expected flag freno_nominas=true")
        passed = len(issues) == 0
        return {
            "pass": passed,
            "score": 1.0 if passed else 0.0,
            "issues": issues,
        }

    # 3. Balance check
    actual_lineas = actual.get("lineas", [])
    if not actual_lineas:
        issues.append("No lines in entry")
        return {"pass": False, "score": 0.0, "issues": issues}

    total_debe = sum(float(linea.get("debe", 0)) for linea in actual_lineas)
    total_haber = sum(float(linea.get("haber", 0)) for linea in actual_lineas)
    diff = total_debe - total_haber
    if abs(diff) > TOLERANCIA:
        issues.append(
            f"Entry out of balance: debe={total_debe:.2f} haber={total_haber:.2f} diff={diff:.2f}"
        )

    # 4. Expected lines vs actual lines (PGC prefix + amount + side)
    matched = 0
    expected_lineas = expected.get("lineas", [])
    for exp in expected_lineas:
        prefix = exp["cuenta_prefijo"]
        exp_debe = float(exp.get("debe", 0))
        exp_haber = float(exp.get("haber", 0))

        found = False
        for act in actual_lineas:
            act_cuenta = str(act.get("cuenta", ""))
            if not act_cuenta.startswith(prefix):
                continue
            act_debe = float(act.get("debe", 0))
            act_haber = float(act.get("haber", 0))
            if abs(act_debe - exp_debe) < TOLERANCIA and abs(act_haber - exp_haber) < TOLERANCIA:
                found = True
                break

        if found:
            matched += 1
        else:
            lado = f"debe={exp_debe:.2f}" if exp_debe > 0 else f"haber={exp_haber:.2f}"
            issues.append(f"Missing line with prefix {prefix}* and {lado}")

    score_lineas = matched / len(expected_lineas) if expected_lineas else 0

    # 5. Semantic flags — exact match
    expected_flags = expected.get("flags", {})
    actual_flags = actual.get("flags", {})
    for flag, exp_val in expected_flags.items():
        act_val = actual_flags.get(flag, False)
        if exp_val != act_val:
            issues.append(f"Flag {flag}: expected {exp_val}, received {act_val}")

    passed = len(issues) == 0
    return {
        "pass": passed,
        "score": score_lineas,
        "issues": issues,
    }


def grade_all(results) -> list[dict]:
    """Accepts a list of results or a full payload dict with 'results' key."""
    if isinstance(results, dict) and "results" in results:
        model = results.get("model", "?")
        timestamp = results.get("timestamp", "?")
        results = results["results"]
        header = f"\nRESULTS · model={model} · timestamp={timestamp}"
    else:
        header = "\nRESULTS"

    grades = []
    for r in results:
        g = grade_caso(r["expected"], r["actual"])
        g["caso_id"] = r["caso_id"]
        g["categoria"] = r.get("categoria", "?")
        grades.append(g)

    passed = sum(1 for g in grades if g["pass"])
    total = len(grades)
    avg_score = sum(g["score"] for g in grades) / total if total else 0

    print(header)
    print("=" * 70)
    print(f"{passed}/{total} cases pass ({100*passed/total:.0f}%) · avg score: {100*avg_score:.0f}%")
    print("=" * 70)

    # Breakdown by category
    cat_stats = defaultdict(lambda: {"pass": 0, "total": 0})
    for g in grades:
        cat_stats[g["categoria"]]["total"] += 1
        if g["pass"]:
            cat_stats[g["categoria"]]["pass"] += 1

    print("\nBy category:")
    for cat, stats in sorted(cat_stats.items()):
        print(f"  {cat:<25} {stats['pass']}/{stats['total']}")

    print("\nDetail:")
    for g in grades:
        emoji = "[OK]" if g["pass"] else "[FAIL]"
        print(f"  {emoji} Case {g['caso_id']:>2} [{g['categoria']}] · score {100*g['score']:.0f}%")
        for issue in g["issues"]:
            print(f"        - {issue}")

    print()
    return grades


def list_results():
    results_dir = Path(__file__).parent / "results"
    if not results_dir.exists():
        print("No results yet. Run: python runner.py")
        return
    files = sorted(results_dir.glob("*.json"))
    if not files:
        print("No results yet. Run: python runner.py")
        return
    print("Available results:")
    for f in files:
        print(f"  {f.relative_to(Path(__file__).parent)}")


def main():
    if len(sys.argv) < 2:
        list_results()
        return
    results_file = Path(sys.argv[1])
    if not results_file.exists():
        print(f"ERROR: file not found: {results_file}")
        sys.exit(1)
    payload = json.loads(results_file.read_text(encoding="utf-8"))
    grade_all(payload)


if __name__ == "__main__":
    main()
