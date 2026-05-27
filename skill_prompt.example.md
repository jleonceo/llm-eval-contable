# Skill Prompt — Example Structure

This file shows the expected structure for `skill_prompt.md`.
Copy this file to `skill_prompt.md` and replace the placeholder content
with your actual system prompt.

`skill_prompt.md` is gitignored — it will never be committed.

---

## Expected Structure

Your system prompt should define:

1. **Role and context** — who the model is and what company/domain it serves
2. **Decision checklist** — ordered steps the model must follow before producing output
3. **Brake conditions** — when to return PENDIENTE_VERIFICACION instead of an entry
4. **Account rules** — specific mappings for your chart of accounts
5. **Examples** — A/B/C worked examples covering common edge cases
6. **Output format** — the exact JSON structure (matches runner.py PROMPT_TEMPLATE)

---

## Minimum Required for the Eval to Work

The system prompt must instruct the model to:

- Return **only JSON** with no surrounding text
- Use the fields: `estado`, `lineas`, `flags`, `concepto`
- Set `estado = "PENDIENTE_VERIFICACION"` and `lineas = []` when data is missing
- Set `freno_nominas = true` for any brake case (not just payroll)
- Use 8-digit account codes
- Balance the entry: Σdebe = Σhaber

---

## Paste your system prompt below this line

[YOUR SYSTEM PROMPT CONTENT HERE]
