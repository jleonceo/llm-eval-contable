"""
Runner del eval contable-experto.
Runner for the contable-experto eval.

Carga un skill prompt desde skill_prompt.md (fichero local, no incluido en el repo),
ejecuta cada caso del dataset contra la API de Claude y guarda los resultados en
results/ con timestamp y nombre de modelo.

Loads a skill prompt from skill_prompt.md (local file, not in repo),
runs each dataset case against the Claude API, and saves results to
results/ with timestamp and model name.

Uso / Usage:
    python runner.py                          # por defecto: claude-sonnet-4-6
    python runner.py --model sonnet           # alias explícito / explicit alias
    python runner.py --model opus
    python runner.py --model haiku
    python runner.py --model claude-opus-4-7  # ID completo / full model ID

Requiere / Requires:
    - ANTHROPIC_API_KEY en .env
    - skill_prompt.md en la raíz del proyecto (copia de skill_prompt.example.md)
      skill_prompt.md in project root (copy from skill_prompt.example.md)
    - dataset_v2.json en la raíz del proyecto / in project root
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    # truststore parchea el SSL de Python para usar el CA store del sistema operativo
    # en lugar del bundle estático de certifi. Necesario en Windows cuando el antivirus
    # (Kaspersky, ESET, Bitdefender, etc.) hace SSL inspection y registra su CA en el
    # sistema pero no en certifi.
    #
    # truststore patches Python's SSL to use the OS certificate store instead of
    # certifi's static bundle. Required on Windows when antivirus software does SSL
    # inspection and registers its CA in the system store but not in certifi.
    import truststore
    truststore.inject_into_ssl()

    from anthropic import Anthropic
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: faltan dependencias / missing dependencies.")
    print("Instala con / Install with: pip install -r requirements.txt")
    sys.exit(1)


def make_anthropic_client() -> Anthropic:
    """Cliente Anthropic usando el CA store del sistema operativo.
    Anthropic client using the OS SSL trust store."""
    return Anthropic()


# Alias cortos → ID completo del modelo en la API
# Short alias → full model ID
MODEL_ALIASES = {
    "sonnet": "claude-sonnet-4-6",
    "opus":   "claude-opus-4-7",
    "haiku":  "claude-haiku-4-5-20251001",
}
DEFAULT_MODEL_ALIAS = "sonnet"

MAX_TOKENS = 2000
TEMPERATURE = 0

# skill_prompt.md vive junto a este fichero (NO se sube al repo).
# Copia skill_prompt.example.md a skill_prompt.md y añade tu system prompt.
#
# skill_prompt.md lives next to this file (NOT committed to the repo).
# Copy skill_prompt.example.md to skill_prompt.md and add your system prompt.
SKILL_PATH = Path(__file__).parent / "skill_prompt.md"
DEFAULT_DATASET = "dataset_v2.json"
RESULTS_DIR = Path(__file__).parent / "results"


PROMPT_TEMPLATE = """Eres un experto contable. Recibes una situación contable y debes proponer el asiento de doble entrada.

Aplica tu checklist contable completo antes de producir el asiento.

Devuelve SOLO un objeto JSON con esta estructura exacta, sin texto adicional antes ni después:

{{
  "estado": "OK" o "PENDIENTE_VERIFICACION",
  "motivo": "solo si estado = PENDIENTE_VERIFICACION",
  "lineas": [
    {{"cuenta": "XXXXXXXX", "nombre_cuenta": "...", "debe": 0.00, "haber": 0.00}}
  ],
  "flags": {{
    "requiere_periodificacion": false,
    "isp": false,
    "freno_nominas": false,
    "retencion_irpf": false
  }},
  "concepto": "narrativa breve del asiento"
}}

Reglas:
- Si el caso requiere freno (PENDIENTE_VERIFICACION), deja "lineas" vacío Y marca freno_nominas: true.
- Σdebe = Σhaber al céntimo.
- Usa cuentas a 8 dígitos. Si el sufijo de empresa es desconocido, usa 'XXXXX' (ej: 62XXXXXX).
- No incluyas ningún texto fuera del JSON.

PREGUNTA DE PRE-VUELO (responde mentalmente antes de escribir el JSON):
¿Falta algún dato imprescindible que NO pueda deducirse del enunciado?
Datos imprescindibles ausentes = freno: importe sin especificar, cuota SS empresa no indicada, % IRPF no indicado, operación sin tipo ni partes identificables.
Datos que SÍ puedes deducir = NO son freno: cuentas contables, tipo IVA estándar 21%, estructura del asiento.
Si falta dato imprescindible: PENDIENTE_VERIFICACION, lineas vacío, freno_nominas: true.
Si tienes todo lo necesario: continúa con el asiento completo.

SITUACIÓN:
{caso_input}
"""


def resolve_model(arg: str) -> tuple[str, str]:
    """Acepta alias corto o ID completo. Devuelve (alias, id_completo).
    Accept short alias or full model ID. Returns (alias, full_id)."""
    if arg in MODEL_ALIASES:
        return arg, MODEL_ALIASES[arg]
    for alias, full_id in MODEL_ALIASES.items():
        if arg == full_id:
            return alias, full_id
    return arg, arg


def load_skill() -> str:
    if not SKILL_PATH.exists():
        print(f"ERROR: skill prompt no encontrado en / not found at: {SKILL_PATH}")
        print("Copia / Copy: skill_prompt.example.md → skill_prompt.md y añade tu system prompt.")
        sys.exit(1)
    return SKILL_PATH.read_text(encoding="utf-8")


def load_dataset(dataset_name: str) -> dict:
    dataset_path = Path(__file__).parent / dataset_name
    if not dataset_path.exists():
        print(f"ERROR: dataset no encontrado en / not found at: {dataset_path}")
        sys.exit(1)
    return json.loads(dataset_path.read_text(encoding="utf-8"))


def parse_response(text: str) -> dict:
    """Parsea la respuesta del modelo como JSON. Devuelve marker de error si falla.
    Parse model response as JSON. Returns error marker on failure."""
    text = text.strip()
    # Quitar code fences si los hay / Remove code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if lines[-1].strip().startswith("```") else "\n".join(lines[1:])
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        return {"_parse_error": str(e), "_raw": text}


def run_eval(model: str, dataset_name: str = DEFAULT_DATASET, verbose: bool = True) -> list[dict]:
    skill_content = load_skill()
    dataset = load_dataset(dataset_name)

    client = make_anthropic_client()

    casos = dataset["casos"]
    results = []
    total_in = 0
    total_out = 0

    # claude-opus-4-7 deprecó el parámetro temperature
    # claude-opus-4-7 deprecated the temperature parameter
    extra_params = {} if model.startswith("claude-opus-4-7") else {"temperature": TEMPERATURE}

    for caso in casos:
        if verbose:
            print(f"  Caso {caso['id']:>2} [{caso['categoria']}] ...", end="", flush=True)

        prompt = PROMPT_TEMPLATE.replace("{caso_input}", caso["input"])

        msg = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=skill_content,
            messages=[{"role": "user", "content": prompt}],
            **extra_params,
        )

        response_text = msg.content[0].text
        actual = parse_response(response_text)

        total_in += msg.usage.input_tokens
        total_out += msg.usage.output_tokens

        results.append({
            "caso_id": caso["id"],
            "categoria": caso["categoria"],
            "descripcion": caso["descripcion"],
            "input": caso["input"],
            "expected": caso["expected"],
            "actual": actual,
            "tokens_input": msg.usage.input_tokens,
            "tokens_output": msg.usage.output_tokens,
        })

        if verbose:
            ok = "_parse_error" not in actual
            print(" OK" if ok else " parse_error")

    if verbose:
        print(f"\n  Tokens totales / Total tokens: input={total_in:,} output={total_out:,}")

    return results


def build_payload(results: list[dict], model_alias: str, model_full: str) -> dict:
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d_%H%M"),
        "model": model_full,
        "model_alias": model_alias,
        "results": results,
    }


def save_payload(payload: dict) -> Path:
    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / f"{payload['timestamp']}_{payload['model_alias']}.json"
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return out_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Runner del eval para skill contable LLM. / Eval runner for accounting LLM skill."
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_ALIAS,
        help=(
            "Modelo a evaluar / Model to evaluate. "
            "Alias: 'sonnet' (defecto/default), 'opus', 'haiku'. "
            "También acepta ID completo / Full model ID also accepted (ej: 'claude-opus-4-7')."
        ),
    )
    parser.add_argument(
        "--dataset",
        default=DEFAULT_DATASET,
        help=f"Fichero de dataset / Dataset filename (defecto/default: {DEFAULT_DATASET}).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # override=True para que .env mande sobre variables de entorno del sistema
    # override=True so .env takes precedence over system environment variables
    load_dotenv(override=True)
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY no encontrada / not found.")
        print("Copia / Copy: .env.example → .env y añade / and add your API key.")
        sys.exit(1)

    model_alias, model_full = resolve_model(args.model)
    print(f"Eval · modelo/model={model_full} (alias={model_alias}) · dataset={args.dataset}\n")

    results = run_eval(model=model_full, dataset_name=args.dataset, verbose=True)

    payload = build_payload(results, model_alias=model_alias, model_full=model_full)
    out_path = save_payload(payload)
    print(f"\n  Resultados guardados en / Results saved to: {out_path}\n")

    from grader import grade_all
    grade_all(payload)


if __name__ == "__main__":
    main()
