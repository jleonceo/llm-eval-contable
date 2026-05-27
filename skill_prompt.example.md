# Skill Prompt — Plantilla / Template

🇪🇸 **Español:** Este fichero muestra la estructura esperada para `skill_prompt.md`.
Cópialo a `skill_prompt.md` y reemplaza el contenido de ejemplo con tu system prompt real.
`skill_prompt.md` está en `.gitignore` — nunca se subirá al repo.

🇬🇧 **English:** This file shows the expected structure for `skill_prompt.md`.
Copy it to `skill_prompt.md` and replace the placeholder content with your actual system prompt.
`skill_prompt.md` is gitignored — it will never be committed.

---

## Estructura esperada / Expected Structure

Tu system prompt debe definir / Your system prompt should define:

1. **Rol y contexto** / **Role and context** — quién es el modelo y en qué dominio opera / who the model is and what domain it serves
2. **Checklist de decisión** / **Decision checklist** — pasos ordenados antes de producir el output / ordered steps the model must follow before producing output
3. **Condiciones de freno** / **Brake conditions** — cuándo devolver PENDIENTE_VERIFICACION / when to return PENDIENTE_VERIFICACION instead of an entry
4. **Reglas de cuentas** / **Account rules** — mapeos específicos para tu plan de cuentas / specific mappings for your chart of accounts
5. **Ejemplos** / **Examples** — casos trabajados A/B/C cubriendo los edge cases más frecuentes / worked examples covering common edge cases
6. **Formato de output** / **Output format** — la estructura JSON exacta (compatible con PROMPT_TEMPLATE en runner.py)

---

## Mínimo requerido para que el eval funcione / Minimum required for the eval to work

El system prompt debe indicar al modelo que / The system prompt must instruct the model to:

- Devolver **solo JSON** sin texto adicional / Return **only JSON** with no surrounding text
- Usar los campos: `estado`, `lineas`, `flags`, `concepto`
- Establecer `estado = "PENDIENTE_VERIFICACION"` y `lineas = []` cuando falten datos / when data is missing
- Marcar `freno_nominas = true` para cualquier caso de freno (no solo nóminas) / for any brake case (not just payroll)
- Usar códigos de cuenta de 8 dígitos / Use 8-digit account codes
- Cuadrar el asiento: Σdebe = Σhaber / Balance the entry: Σdebit = Σcredit

---

## Añade tu system prompt aquí / Paste your system prompt below this line

[TU SYSTEM PROMPT AQUÍ / YOUR SYSTEM PROMPT HERE]
