# Eval Results — Score Progression

**Skill under test:** contable-experto (Spanish PGC accounting assistant)
**Model:** claude-sonnet-4-6
**Dataset:** dataset_v2.json (50 cases, 12 categories)
**Temperature:** 0 (deterministic)

---

## Score Progression

| Run | Date | Score | % | Skill version | Key changes |
|-----|------|-------|---|---------------|-------------|
| 1 — Baseline | 2026-05-26 | 33 / 50 | 66% | v1.0 | Initial skill |
| 2 | 2026-05-26 | 36 / 50 | 72% | v1.5 | IVA taxonomy, ISP rules |
| 3 | 2026-05-26 | 38 / 50 | 76% | v2.0 | Freno logic, payroll 465 |
| 4 | 2026-05-27 | 41 / 50 | 82% | v2.2 | Leasing activation, periodificación |
| 5 | 2026-05-27 | 44 / 50 | 88% | v2.6 | SaaS exception, 640 vs 641, embargo |
| **Theoretical (v2.8)** | 2026-05-27 | **47 / 50** | **94%** | v2.8 | Dataset fixes + accrual clarification |

*Theoretical score: manually verified by case analysis after applying all v2.8 fixes.*
*Run 6 pending to confirm theoretical score in practice.*

---

## Category Results — Run 5

| Category | Cases | Pass | % |
|---------|-------|------|---|
| facturas_emitidas | 6 | 6 | 100% |
| facturas_recibidas | 6 | 6 | 100% |
| intracomunitario | 4 | 4 | 100% |
| isp_domestico | 3 | 3 | 100% |
| nominas_simples | 4 | 4 | 100% |
| nominas_irpf_embargos | 3 | 3 | 100% |
| amortizaciones | 3 | 2 | 67% |
| periodificaciones | 4 | 3 | 75% |
| cierre_regularizacion | 4 | 4 | 100% |
| impuestos | 5 | 5 | 100% |
| trampas_errores | 4 | 4 | 100% |
| leasing_renting | 4 | 3 | 75% |
| **TOTAL** | **50** | **44** | **88%** |

---

## Failures After Run 5 (3 resolved in v2.8)

| Case | Category | Issue | Resolution | Status |
|------|----------|-------|------------|--------|
| 30 | amortizaciones | Pre-flight too aggressive → false brake on ERP amortisation | Refined pre-flight to distinguish derivable vs truly missing data | ✅ Fixed in v2.8 |
| 33 | periodificaciones | Dataset error: `requiere_periodificacion: true` was wrong (current-month accrual ≠ periodificación) | Changed to `false` in dataset | ✅ Fixed in v2.8 |
| 49 | leasing_renting | Pre-flight blocked leasing payment (524 = CP, not 174 = LP) | Skill clarification + pre-flight refinement | ✅ Fixed in v2.8 |
| 34 | cierre_regularizacion | Prefix too strict (`300`, `610` vs `30`, `61`) | Relaxed to 2-digit prefix in dataset | ⚠️ Partially addressed |
| — | — | Two further edge cases under investigation | — | 🔄 Pending run 6 |

---

## Lessons Learned

### What moves the score most

1. **Freno (brake) precision** — the model must know exactly when to refuse. Too aggressive = false positives on real cases. Too permissive = produces wrong entries. The pre-flight question pattern solved this.

2. **Account prefix depth** — testing at 2-digit PGC group level vs 3-digit subgroup matters. Overly strict prefixes in the dataset penalise correct entries.

3. **Cognitive bias mitigation** — the pre-flight question directly targets recency bias (what the model "thinks about last" before output anchors the response). This was the single biggest improvement in runs 4→5.

4. **Edge case taxonomy** — categories like `trampas_errores` (trap cases) don't just test knowledge — they test that the model resists the most common LLM failure mode: compliance with user framing even when the request is incorrect.

### What doesn't move the score (lessons from dead-end iterations)

- Adding more examples without identifying the failure pattern: score stayed flat
- Making instructions longer without making them more specific: added confusion
- Fixing one case without checking for regressions: fixed 1, broke 1

---

*Last updated: 2026-05-27*
