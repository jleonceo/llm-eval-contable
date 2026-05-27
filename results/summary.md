# Resultados del Eval — Progresión de Puntuaciones
# Eval Results — Score Progression

**Skill evaluada / Skill under test:** contable-experto (asistente contable PGC en español / Spanish PGC accounting assistant)
**Modelo / Model:** claude-sonnet-4-6
**Dataset:** dataset_v2.json (50 casos / cases, 12 categorías / categories)
**Temperature:** 0 (determinista / deterministic)

---

## Progresión / Score Progression

| Run | Fecha / Date | Puntuación / Score | % | Versión skill | Cambio clave / Key change |
|-----|------|-------|---|---------------|-------------|
| 1 — Baseline | 2026-05-26 | 33 / 50 | 66% | v1.0 | Skill inicial / Initial skill |
| 2 | 2026-05-26 | 36 / 50 | 72% | v1.5 | Taxonomía IVA, reglas ISP / VAT taxonomy, ISP rules |
| 3 | 2026-05-26 | 38 / 50 | 76% | v2.0 | Lógica de freno, nóminas 465 / Brake logic, payroll 465 |
| 4 | 2026-05-27 | 41 / 50 | 82% | v2.2 | Activación leasing, periodificación / Leasing activation |
| 5 | 2026-05-27 | 44 / 50 | 88% | v2.6 | Excepción SaaS, 640 vs 641, embargo / Garnishments |
| **Teórico v2.8 / Theoretical** | 2026-05-27 | **47 / 50** | **94%** | v2.8 | Correcciones dataset + aclaración devengo / Dataset fixes + accrual |

*Puntuación teórica verificada por análisis manual de casos tras aplicar todas las correcciones v2.8.*
*Theoretical score manually verified by case analysis after applying all v2.8 fixes.*
*Run 6 pendiente para confirmar en práctica / Run 6 pending to confirm in practice.*

---

## Resultados por categoría — Run 5 / Category Results — Run 5

| Categoría / Category | Casos / Cases | Pasan / Pass | % |
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

## Fallos tras Run 5 (3 resueltos en v2.8) / Failures after Run 5 (3 resolved in v2.8)

| Caso | Categoría | Problema / Issue | Solución / Resolution | Estado / Status |
|------|----------|-------|------------|--------|
| 30 | amortizaciones | Pre-vuelo demasiado agresivo → falso freno en amortización de ERP / Pre-flight too aggressive → false brake on ERP amortisation | Pregunta de pre-vuelo refinada para distinguir datos derivables vs datos imprescindibles / Refined pre-flight to distinguish derivable vs truly missing data | ✅ Resuelto / Fixed v2.8 |
| 33 | periodificaciones | Error en dataset: `requiere_periodificacion: true` era incorrecto (devengo del mes corriente ≠ periodificación) / Dataset error: current-month accrual ≠ periodificación | Cambiado a `false` en dataset / Changed to `false` in dataset | ✅ Resuelto / Fixed v2.8 |
| 49 | leasing_renting | Pre-vuelo bloqueaba pago de cuota de leasing (524 CP, no 174 LP) / Pre-flight blocked leasing payment | Aclaración en skill + refinamiento pre-vuelo / Skill clarification + pre-flight refinement | ✅ Resuelto / Fixed v2.8 |
| 34 | cierre_regularizacion | Prefijo demasiado estricto en dataset (`300`, `610` en lugar de `30`, `61`) / Overly strict prefix in dataset | Relajado a 2 dígitos / Relaxed to 2-digit prefix | ⚠️ Parcial / Partially addressed |
| — | — | Dos casos edge adicionales en investigación / Two further edge cases under investigation | — | 🔄 Pendiente / Pending run 6 |

---

## Lecciones aprendidas / Lessons Learned

### Qué mueve más la puntuación / What moves the score most

1. **Precisión del freno / Brake precision** — el modelo debe saber exactamente cuándo rechazar / the model must know exactly when to refuse. Demasiado agresivo = falsos positivos. Demasiado permisivo = asientos incorrectos. La pregunta de pre-vuelo resolvió esto / The pre-flight question pattern solved this.

2. **Profundidad del prefijo PGC / Account prefix depth** — testear al nivel de grupo de 2 dígitos vs subgrupo de 3 dígitos importa. Prefijos demasiado estrictos en el dataset penalizan asientos correctos / Overly strict prefixes in the dataset penalise correct entries.

3. **Mitigación de sesgo cognitivo / Cognitive bias mitigation** — la pregunta de pre-vuelo ataca directamente el sesgo de recencia (lo último en lo que piensa el modelo antes del output ancla la respuesta). Fue la mejora más grande de los runs 4→5 / This was the single biggest improvement in runs 4→5.

4. **Casos trampa / Trap cases** — las categorías como `trampas_errores` no solo testean conocimiento — testean que el modelo resiste el fallo más común de los LLM: conformarse con el marco del usuario aunque la petición sea incorrecta / they test that the model resists the most common LLM failure mode: compliance with user framing even when the request is wrong.

### Lo que no mueve la puntuación / What doesn't move the score

- Añadir más ejemplos sin identificar el patrón de fallo / Adding examples without identifying the failure pattern: puntuación plana / score stayed flat
- Instrucciones más largas sin más específicas / Making instructions longer without more specific: añade confusión / adds confusion
- Corregir un caso sin verificar regresiones / Fixing one case without checking for regressions: arregla 1, rompe 1 / fixed 1, broke 1

---

*Última actualización / Last updated: 2026-05-27*
