"""Runner for the contable-experto eval.

Loads a skill prompt from skill_prompt.md (local file, not included in repo),
runs each case in the dataset against the Claude API, and saves results to
results/ with timestamp and model name.

Usage:
    python runner.py                          # default: claude-sonnet-4-6
    python runner.py --model sonnet           # explicit alias
    python runner.py --model opus
    python runner.py --model haiku
    python runner.py --model claude-opus-4-7  # full model ID also works

Requires:
    - ANTHROPIC_API_KEY in .env
    - skill_prompt.md in the project root  (copy from skill_prompt.example.md)
    - dataset_v2.json in the project root
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    # truststore patches Python's SSL to use the OS certificate store instead
    # of certifi's static bundle. Required on Windows when antivirus software
    # (Kaspersky, ESET, Bitdefender, etc.) does SSL inspection and registers
    # its own CA in the system store but not in certifi.
    import truststore
    truststore.inject_into_ssl()

    from anthropic import Anthropic
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: missing dependencies. Install with:")
    print("    pip install -r requirements.txt")
    sys.exit(1)


def make_anthropic_client() -> Anthropic:
    """Anthropic client using OS SSL trust store."""
    return Anthropic()


# Short alias → full model ID
MODEL_ALIASES = {
    "sonnet": "claude-sonnet-4-6",
    "opus":   "claude-opus-4-7",
    "haiku":  "claude-haiku-4-5-20251001",
}
DEFAULT_MODEL_ALIAS = "sonnet"

MAX_TOKENS = 2000
TEMPERATURE = 0

# skill_prompt.md lives next to this file (NOT committed to the repo).
# Copy skill_prompt.example.md to skill_prompt.md and add your system prompt.
SKILL_PATH = Path(__file__).parent / "skill_prompt.md"
DEFAULT_DATASET = "dataset_v2.json"
RESULTS_DIR = Path(__file__).parent / "results"


PROMPT_TEMPLATE = """You are an accounting expert. You receive an accounting situation and must propose the double-entry bookkeeping entry.

Apply your complete accounting checklist before producing the entry.

Return ONLY a JSON object with this exact structure, no additional text before or after:

{{
  "estado": "OK" or "PENDIENTE_VERIFICACION",
  "motivo": "only if estado = PENDIENTE_VERIFICACION",
  "lineas": [
    {{"cuenta": "XXXXXXXX", "nombre_cuenta": "...", "debe": 0.00, "haber": 0.00}}
  ],
  "flags": {{
    "requiere_periodificacion": false,
    "isp": false,
    "freno_nominas": false,
    "retencion_irpf": false
  }},
  "concepto": "brief description of the entry"
}}

Rules:
- If the case requires a brake (PENDIENTE_VERIFICACION), leave "lineas" empty AND set freno_nominas: true.
- Sigma(debe) = Sigma(haber) to the cent.
- Use 8-digit account codes. If the company suffix is unknown, use 'XXXXX' (e.g. 62XXXXXX).
- Do not include any text outside the JSON.

PRE-FLIGHT CHECK (answer mentally before writing the JSON):
Is there any essential data that CANNOT be derived from the description?
Essential missing data = brake: unspecified amount, employer SS rate not given, IRPF % not given, operation with no identifiable type or parties.
Data you CAN derive = NOT a brake: account codes, standard 21% VAT, entry structure.
If essential data is missing: PENDIENTE_VERIFICACION, empty lineas, freno_nominas: true.
If you have everything needed: proceed with the complete entry.

SITUATION:
{caso_input}
"""


def resolve_model(arg: str) -> tuple[str, str]:
    """Accept short alias or full model ID. Returns (alias, full_id)."""
    if arg in MODEL_ALIASES:
        return arg, MODEL_ALIASES[arg]
    for alias, full_id in MODEL_ALIASES.items():
        if arg == full_id:
            return alias, full_id
    return arg, arg


def load_skill() -> str:
    if not SKILL_PATH.exists():
        print(f"ERROR: skill prompt not found at {SKILL_PATH}")
        print("Copy skill_prompt.example.md to skill_prompt.md and add your system prompt.")
        sys.exit(1)
    return SKILL_PATH.read_text(encoding="utf-8")


def load_dataset(dataset_name: str) -> dict:
    dataset_path = Path(__file__).parent / dataset_name
    if not dataset_path.exists():
        print(f"ERROR: dataset not found at {dataset_path}")
        sys.exit(1)
    return json.loads(dataset_path.read_text(encoding="utf-8"))


def parse_response(text: str) -> dict:
    """Parse model response as JSON. Returns error marker on failure."""
    text = text.strip()
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

    # claude-opus-4-7 deprecated the temperature parameter
    extra_params = {} if model.startswith("claude-opus-4-7") else {"temperature": TEMPERATURE}

    for caso in casos:
        if verbose:
            print(f"  Case {caso['id']:>2} [{caso['categoria']}] ...", end="", flush=True)

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
        print(f"\n  Total tokens: input={total_in:,} output={total_out:,}")

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
        description="Eval runner for accounting LLM skill."
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_ALIAS,
        help=(
            "Model to evaluate. Short aliases: 'sonnet' (default), 'opus', 'haiku'. "
            "Full model ID also accepted (e.g. 'claude-opus-4-7')."
        ),
    )
    parser.add_argument(
        "--dataset",
        default=DEFAULT_DATASET,
        help=f"Dataset filename (default: {DEFAULT_DATASET}).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # override=True so .env takes precedence over any system env variable
    load_dotenv(override=True)
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not found.")
        print("Copy .env.example to .env and add your API key.")
        sys.exit(1)

    model_alias, model_full = resolve_model(args.model)
    print(f"Eval · model={model_full} (alias={model_alias}) · dataset={args.dataset}\n")

    results = run_eval(model=model_full, dataset_name=args.dataset, verbose=True)

    payload = build_payload(results, model_alias=model_alias, model_full=model_full)
    out_path = save_payload(payload)
    print(f"\n  Results saved to: {out_path}\n")

    from grader import grade_all
    grade_all(payload)


if __name__ == "__main__":
    main()
