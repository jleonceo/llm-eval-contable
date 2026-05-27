# LLM Eval — Contable Experto
**Automated evaluation framework for a Spanish PGC accounting LLM skill**

> 50 test cases · 12 categories · 5 iterations · **66% → 94% accuracy** · AI cognitive bias mitigation

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Model: Claude Sonnet](https://img.shields.io/badge/Model-Claude%20Sonnet%204.6-orange.svg)](https://anthropic.com)

---

## What This Is

An eval-driven development pipeline to test, measure, and iteratively improve an LLM-based accounting assistant. The skill under test generates Spanish double-entry bookkeeping entries (PGC — *Plan General Contable*) from natural language descriptions.

**The insight behind this project:** improving an LLM skill is not about writing more instructions — it's about measuring failure patterns systematically, fixing the root cause, and verifying fixes don't break passing cases (regression testing).

---

## Score Progression

| Run | Score | Accuracy | Key change |
|-----|-------|----------|------------|
| Run 1 — baseline | 33 / 50 | 66% | Initial skill v1.0 |
| Runs 2–3 | 36–38 / 50 | 72–76% | Taxonomy fixes, IVA rules |
| Run 4 | 41 / 50 | 82% | Freno logic, payroll edge cases |
| Run 5 | 44 / 50 | 88% | SaaS exception, 640 vs 641, embargo |
| **Theoretical (v2.8)** | **47 / 50** | **94%** | Dataset corrections + skill refinements |

*Theoretical score verified by manual analysis of remaining failures after applying all v2.8 fixes.*

---

## Test Coverage — 50 Cases, 12 Categories

| Category | Cases | What it tests |
|---------|-------|---------------|
| `facturas_emitidas` | 6 | B2B credit sales, B2C cash, discounts, returns, advances, collections |
| `facturas_recibidas` | 6 | Purchases, service payments, rappels, advance suppliers |
| `intracomunitario` | 4 | Intra-EU purchases/sales, ISP (reverse charge), VAT exemptions |
| `isp_domestico` | 3 | Domestic reverse charge: construction works, rental |
| `nominas_simples` | 4 | Payroll accrual (640/642/465/476), extra pay, bank transfer |
| `nominas_irpf_embargos` | 3 | High IRPF, judicial garnishments (410 + 465 coexist) |
| `amortizaciones` | 3 | Tangible assets (681/281), intangible assets (680/280) |
| `periodificaciones` | 4 | Prepaid expenses (480), deferred income (485), accruals |
| `cierre_regularizacion` | 4 | Inventory adj., impairment, result transfer, reversals |
| `impuestos` | 5 | VAT settlement (303), IRPF payments (111/115), compensation |
| `trampas_errores` | 4 | VAT-inclusive price traps, missing data triggers, unbalanced entries |
| `leasing_renting` | 4 | Renting (operating lease), leasing activation, monthly payments |

---

## How the Eval Works

### Architecture

```
dataset_v2.json          ← 50 test cases with expected outputs
     │
     ▼
runner.py  ──────────────── loads skill_prompt.md as system prompt
     │                ───── calls Claude API (temperature=0)
     │                ───── parses JSON response
     ▼
results/YYYY-MM-DD_HHMM_sonnet.json   ← raw output per case
     │
     ▼
grader.py  ──────────────── validates: account prefix match
                       ───── validates: amount ± €0.01 tolerance
                       ───── validates: balance (Σdebe = Σhaber)
                       ───── validates: semantic flags
                       ───── reports by category
```

### What the Grader Checks

1. **Estado** — OK vs PENDIENTE_VERIFICACION (mandatory brake when data is missing)
2. **Balance** — total DEBE must equal total HABER (±€0.01)
3. **Account lines** — each expected line must match by **PGC prefix** (not exact code), amount, and debit/credit side
4. **Semantic flags** — `requiere_periodificacion`, `isp`, `freno_nominas`, `retencion_irpf`

The prefix-based matching (`startswith`) is key: the skill uses 8-digit company-specific codes (e.g. `62000001`), but the test only requires the correct PGC group (e.g. `62`). This tests accounting knowledge, not memorisation.

---

## AI Cognitive Bias Mitigation

The most interesting part of this project was applying **cognitive bias theory directly to prompt engineering**. Six biases were identified and addressed:

### 1. Recency Bias
*Problem:* the model's last "thought" before generating output anchors the response. If the most recent context is a positive example, the model leans permissive.

*Fix:* Added a **pre-flight question** as the final instruction before the input — forcing the model to check for missing critical data (missing IRPF %, undeclared employer SS contribution) before writing any JSON.

### 2. Confirmation Bias
*Problem:* the model confirms the frame set by the question. "Contabiliza esta factura..." primes it to produce an entry, even when data is insufficient.

*Fix:* Added an **8-step checklist** the model must run before producing the entry. The checklist resets the frame from "produce output" to "verify first".

### 3. Anchoring Bias
*Problem:* the first account mentioned in the description anchors the model's choice, even when wrong.

*Fix:* The prompt explicitly lists categories where the "obvious" account is wrong (SaaS subscriptions → 62x not 20x, payroll accrual → 465 not 572).

### 4. False Balance Bias
*Problem:* when two accounting treatments are possible, the model hedges and picks the "average" — producing a hybrid entry that's wrong under both criteria.

*Fix:* Hard rules with decision criteria. No "it could be either" — the prompt forces a binary decision based on explicit conditions (e.g. is the service period > 1 month? → mandatory periodificación).

### 5. Sycophancy
*Problem:* when the user's input implies an expected result (e.g. "make this entry: DEBE 600 / HABER 400"), the model complies even when it's wrong (unbalanced).

*Fix:* The grader includes explicit **trap cases** (cases 43–46) where the correct answer is to refuse and return PENDIENTE_VERIFICACION.

### 6. Cherry Picking
*Problem:* the model selects the most favourable interpretation of ambiguous data instead of flagging the ambiguity.

*Fix:* The pre-flight question distinguishes **truly derivable data** (standard 21% VAT, account structure) from **data that must be given** (IRPF %, employer SS rate, operation amount). Ambiguous data triggers the brake.

---

## How to Use This Framework

### Prerequisites

```bash
# Python 3.10+, Conda recommended
conda create -n llm-eval python=3.10
conda activate llm-eval
pip install -r requirements.txt
```

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/jleonceo/llm-eval-contable.git
cd llm-eval-contable

# 2. Set your API key
cp .env.example .env
# Edit .env: ANTHROPIC_API_KEY=your_key_here

# 3. Add your skill prompt
cp skill_prompt.example.md skill_prompt.md
# Edit skill_prompt.md with your actual system prompt
```

### Run the eval

```bash
# Default: Claude Sonnet 4.6
python runner.py

# Explicit model
python runner.py --model sonnet
python runner.py --model opus
python runner.py --model haiku

# Grade an existing result
python grader.py results/2026-05-27_1200_sonnet.json
```

### Adapt for your own skill

The dataset expects JSON output with this structure:

```json
{
  "estado": "OK",
  "lineas": [
    {"cuenta": "47200001", "nombre_cuenta": "IVA soportado", "debe": 21.00, "haber": 0.00}
  ],
  "flags": {
    "requiere_periodificacion": false,
    "isp": false,
    "freno_nominas": false,
    "retencion_irpf": false
  }
}
```

Replace `skill_prompt.md` with your system prompt. Adjust `dataset_v2.json` for your test cases. The `grader.py` logic is generic and reusable.

---

## File Structure

```
llm-eval-contable/
├── README.md                   ← this file
├── dataset_v2.json             ← 50 test cases with expected outputs
├── grader.py                   ← evaluation and scoring logic
├── runner.py                   ← API runner (loads skill_prompt.md)
├── skill_prompt.md             ← your system prompt (NOT included — see .gitignore)
├── skill_prompt.example.md     ← template showing required structure
├── requirements.txt
├── .env.example
├── .gitignore
└── results/
    └── summary.md              ← score progression across runs
```

---

## Key Technical Decisions

**Why prefix-based account matching?**
The PGC uses a hierarchical chart of accounts. Companies extend with their own suffixes (e.g. `47200001` for a specific VAT account). Testing exact codes would make the eval brittle and company-specific. Prefix matching (`62x` = any expense account) tests the accounting knowledge that actually matters.

**Why temperature=0?**
Reproducibility. At temperature > 0, the same case can pass or fail across runs for random reasons, making it impossible to attribute score changes to prompt changes. Zero temperature makes each run deterministic.

**Why JSON output?**
Structured output enables automated grading. Free-text accounting explanations are useful for humans but impossible to grade at scale. The JSON format also forces the model to be precise about amounts (no rounding in prose).

**Why a mandatory brake (PENDIENTE_VERIFICACION)?**
A wrong entry in an accounting system is worse than no entry. The brake pattern — refuse and explain rather than guess — is the right behaviour for a production accounting assistant.

---

## Results Detail

See [`results/summary.md`](results/summary.md) for the full progression analysis with category breakdowns.

---

## Author

**Juan Luis León Rodríguez**
Data Analyst · Business Intelligence · Applied AI

- 💼 [LinkedIn](https://linkedin.com/in/jlleonrodriguez/)
- 🐙 [GitHub](https://github.com/jleonceo)
- 🌐 [Portfolio](https://juanluisleon.vercel.app)

---

## License

MIT — see [LICENSE](LICENSE). Attribution appreciated.

---

*Built with Claude Sonnet 4.6 · May 2026*
