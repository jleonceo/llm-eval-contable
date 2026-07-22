# LLM Eval de la skill Contable Experto

**Framework de evaluación automática para una skill contable en LLM**
*Automated evaluation framework for a Spanish PGC accounting LLM skill*

> 50 casos de test · 12 categorías · 6 iteraciones · **66% → 100% medido** · Mitigación de sesgos cognitivos en IA
> *50 test cases · 12 categories · 6 iterations · **66% → 100% measured** · AI cognitive bias mitigation*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Model: Claude Sonnet](https://img.shields.io/badge/Model-Claude%20Sonnet%204.6-orange.svg)](https://anthropic.com)

---

 [Español](#español) ·  [English](#english)

---

<a name="español"></a>
## Español

### Qué es esto

Un pipeline de **desarrollo orientado a evaluación** para medir y mejorar iterativamente una skill LLM de contabilidad. La skill bajo test genera asientos contables de doble entrada (PGC, *Plan General Contable* español) a partir de descripciones en lenguaje natural.

**La idea central:** mejorar una skill de LLM no es cuestión de escribir más instrucciones, es medir los patrones de fallo de forma sistemática, corregir la causa raíz, y verificar que las correcciones no rompen los casos que ya pasaban (regresión).

---

### Si empiezas de cero: ¿qué es una skill y por qué examinarla?

Imagina que contratas a un especialista. El primer día le das un manual con cómo se trabaja en tu casa: tus reglas, tus casos especiales, los errores que no puede cometer y el formato en el que entrega. Eso es una **skill**: el manual de instrucciones que convierte una IA genérica en un especialista de tu tarea concreta.

El problema viene después, aunque casi nadie habla de él: **¿cómo sabes que tu especialista hace bien su trabajo?** Una IA siempre responde con seguridad, acierte o no. Si le pides un asiento contable, te lo da; que sea correcto es otra historia. Fiarse de la sensación ("parece que va bien") es la receta para llevarse sorpresas justo donde más duele.

Este repositorio resuelve eso con la herramienta más vieja del mundo: **un examen**. 50 casos con su respuesta correcta conocida, un corrector automático que puntúa sin piedad, y una regla de oro, cuando un caso falla, se corrige la skill y se repite el examen *entero*, para comprobar que el arreglo no ha roto lo que ya funcionaba. La skill pasó de aprobar el 66% del examen a aprobarlo entero. No porque la IA mejorase: porque el manual mejoró, medido fallo a fallo.

---

### Progresión de resultados

| Run | Puntuación | % | Versión skill | Cambio principal |
|-----|-----------|---|---------------|-----------------|
| Run 1, baseline | 33 / 50 | 66% | v1.0 | Skill inicial |
| Runs 2-3 | 36-38 / 50 | 72-76% | v1.5-v2.0 | Taxonomía IVA, reglas ISP |
| Run 4 | 41 / 50 | 82% | v2.2 | Freno, asientos de nómina |
| Run 5 | 44 / 50 | 88% | v2.6 | Excepción SaaS, 640 vs 641, embargo |
| **Run 6, final** | **50 / 50** | **100%** | v3.0 | Correcciones dataset + periodificación pasiva y traspaso a reservas (ejemplos F y G) |

*Run 6 ejecutado el 28/05/2026. El resultado completo está en [`results/2026-05-28_1654_sonnet.json`](results/2026-05-28_1654_sonnet.json), re-puntuable con `grader.py`.*

*Matiz honesto: el 100% es sobre **este** examen de 50 casos. No significa que la skill sea infalible, significa que ya no falla ninguno de los patrones que el examen cubre. Ampliar el examen es la forma de volver a encontrar fallos.*

> ### ⚠️ El examen cambió el 20/07/2026, así que el 100% de arriba ya no le corresponde
>
> Una auditoría del dataset encontró que **el caso 21 enseñaba un tratamiento fiscal que no
> existe**. Planteaba el alquiler de un local de negocio como inversión del sujeto pasivo por
> "renuncia a la exención". Verificado contra la AEAT y el BOE:
>
> - El alquiler de local **no está exento** de IVA: la exención del art. 20.Uno.23º LIVA es
>   para viviendas. Sin exención no hay nada a lo que renunciar.
> - El art. 84.Uno.2.e, que el caso invocaba, se aplica a **entregas** de inmuebles
>   (compraventas), no a arrendamientos, y solo alcanza a las exenciones 20º y 22º.
> - Faltaba la **retención del 19 % de IRPF** sobre el alquiler.
>
> Lo delata el propio examen: el **caso 42** dice que se retuvieron 684 € en un trimestre.
> 684 / 0,19 = 3.600 = 3 × 1.200 €, exactamente la renta del caso 21. El dataset daba por
> retenido lo que el caso 21 negaba.
>
> El caso 21 está corregido (alquiler con IVA repercutido + retención). **La consecuencia es
> que la tabla de arriba mide un examen que ya no es este**: el 100 % corresponde a la versión
> anterior. Hasta que se repita la serie completa, léela como historia del proceso, no como
> el resultado vigente.
>
> **El caso 20 tenía el mismo problema, y uno peor encima.** Planteaba una reforma de mejora de
> 5.000 € como inversión del sujeto pasivo. La letra f) del art. 84.Uno.2º solo alcanza a
> urbanización, construcción o **rehabilitación**, y "rehabilitación" es un concepto tasado
> (art. 20.Uno.22º.B): exige que más del 50 % del coste sea obra estructural **y** que el total
> supere el 25 % del valor del inmueble neto de suelo. Para que 5.000 € superaran ese 25 %, el
> local tendría que valer menos de 20.000 €.
>
> Lo peor no era el error de fondo: **el enunciado dictaba la respuesta**. Decía literalmente
> *"aplica ISP obligatorio (art. 84.1.2.f LIVA)"* dentro del input. Así el caso no medía si el
> modelo conoce la norma, medía si obedece una premisa falsa que se le entrega. Reescrito para
> dar los hechos (tipo de obra, valor del local) y que el modelo tenga que decidir.
>
> Comprobado tras la corrección: los 50 casos cuadran (debe = haber) y **ningún enunciado dicta
> ya su propia respuesta**.
>
> Y el fallo de fondo que esto enseña, que es más útil que el caso: un examen puede estar
> **internamente consistente y externamente equivocado**. El corrector cuadraba, los importes
> cuadraban, el asiento cuadraba, y aun así premiaba una respuesta que la ley no admite. Lo cazó
> cotejar la fuente primaria, no volver a mirar el examen.

---

### Cobertura: 50 casos en 12 categorías

| Categoría | Casos | Qué testea |
|---------|-------|------------|
| `facturas_emitidas` | 6 | Ventas B2B a crédito, B2C al contado, descuentos, devoluciones, anticipos, cobros |
| `facturas_recibidas` | 6 | Compras, pagos de servicios, rappels, anticipos a proveedores |
| `intracomunitario` | 4 | Adquisiciones/entregas intracomunitarias, ISP, exenciones IVA |
| `isp_domestico` | 3 | ISP doméstico: ejecución de obras, arrendamiento con renuncia a exención |
| `nominas_simples` | 4 | Devengo nómina (640/642/465/476), paga extra, pago en banco |
| `nominas_irpf_embargos` | 3 | IRPF elevado, embargo judicial (410 + 465 coexisten) |
| `amortizaciones` | 3 | Inmovilizado material (681/281), intangible (680/280) |
| `periodificaciones` | 4 | Gastos anticipados (480), ingresos diferidos (485), accruals |
| `cierre_regularizacion` | 4 | Variación existencias, deterioro, traspaso resultado, reversión |
| `impuestos` | 5 | Liquidación IVA (303), pagos IRPF (111/115), compensación |
| `trampas_errores` | 4 | IVA sobre precio total, datos insuficientes, asientos descuadrados |
| `leasing_renting` | 4 | Renting (gasto corriente), activación leasing, cuotas mensuales |

---

### Cómo funciona el examen

Un **eval** es un examen automático a un modelo de lenguaje: se le pasan siempre los mismos casos,
con la respuesta correcta escrita de antemano, y un programa compara lo que contesta con lo que
debía contestar. Sirve para saber si una versión nueva mejora o empeora, en vez de decidirlo por la
impresión que dan cuatro pruebas sueltas.

#### Las tres piezas

```
dataset_v2.json          ← 50 casos, cada uno con su respuesta correcta
     │
     ▼
runner.py  ──────────────── carga skill_prompt.md como instrucciones del modelo
     │                ───── llama a la API de Claude (temperature=0, sin azar)
     │                ───── interpreta la respuesta, que viene en formato JSON
     ▼
results/AAAA-MM-DD_HHMM_sonnet.json   ← lo que contestó, caso a caso, sin retocar
     │
     ▼
grader.py  ──────────────── valida: coincidencia por prefijo PGC
                       ───── valida: importes ±€0,01 de tolerancia
                       ───── valida: cuadre (Σdebe = Σhaber)
                       ───── valida: flags semánticos
                       ───── reporta por categoría
```

El **corrector** (`grader.py`) es la pieza que pone la nota. Trabaja sobre lo ya guardado, así que
puede volver a puntuar un examen antiguo sin gastar una sola llamada al modelo.

#### Qué verifica el corrector

1. **Estado**, OK vs PENDIENTE_VERIFICACION (freno obligatorio cuando faltan datos)
2. **Cuadre**, total DEBE debe igualar total HABER (±€0,01)
3. **Líneas del asiento**, cada línea esperada debe coincidir por **prefijo PGC**, importe y lado
   (debe o haber). Prefijo significa que basta con acertar la familia de la cuenta del Plan General
   Contable: si la respuesta correcta es la 4300 y el modelo escribe 43000002, se da por buena,
   porque las dos son «clientes» y el dígito final depende de cómo tenga cada empresa su plan.
4. **Flags semánticos**, `requiere_periodificacion`, `isp`, `freno_nominas`, `retencion_irpf`

La validación por prefijo (`startswith`) es clave: la skill usa códigos de 8 dígitos específicos de empresa (ej. `47200001`), pero el test solo exige el grupo PGC correcto (ej. `472`). Esto testea el conocimiento contable, no la memorización de códigos.

---

### Mitigación de sesgos cognitivos en IA

La parte más interesante del proyecto fue aplicar **teoría de sesgos cognitivos directamente al diseño del prompt**. Se identificaron y abordaron seis sesgos:

#### 1. Sesgo de recencia
*Problema:* el último "pensamiento" del modelo antes de generar output ancla la respuesta. Si el contexto más reciente es un ejemplo positivo, el modelo se vuelve permisivo.

*Solución:* se añadió una **pregunta de pre-vuelo** como última instrucción antes del input, forzando al modelo a verificar si faltan datos críticos (% IRPF, cuota SS empresa) antes de escribir ningún JSON.

#### 2. Sesgo de confirmación
*Problema:* el modelo confirma el marco establecido por la pregunta. "Contabiliza esta factura..." lo predispone a producir un asiento aunque los datos sean insuficientes.

*Solución:* se añadió un **checklist de 8 pasos** que el modelo debe ejecutar antes de producir el asiento. El checklist resetea el marco de "produce output" a "verifica primero".

#### 3. Sesgo de anclaje
*Problema:* la primera cuenta mencionada en la descripción ancla la elección del modelo, aunque sea incorrecta.

*Solución:* reglas explícitas para categorías donde la cuenta "obvia" es incorrecta (suscripciones SaaS → 62x no 20x, devengo nómina → 465 no 572).

#### 4. Falso equilibrio
*Problema:* cuando existen dos tratamientos contables posibles, el modelo elige el "término medio", produciendo un asiento híbrido incorrecto bajo ambos criterios.

*Solución:* reglas binarias con criterios de decisión explícitos. Sin "podría ser cualquiera de los dos", el prompt fuerza una decisión basada en condiciones concretas.

#### 5. Servilismo (*sycophancy*)
*Problema:* cuando el input del usuario implica un resultado esperado (ej. "haz este asiento: DEBE 600 / HABER 400"), el modelo cumple aunque sea incorrecto (descuadrado).

*Solución:* **casos trampa** en el dataset (casos 43-46) donde la respuesta correcta es rechazar y devolver PENDIENTE_VERIFICACION.

#### 6. *Cherry picking*
*Problema:* el modelo selecciona la interpretación más favorable de datos ambiguos en lugar de señalar la ambigüedad.

*Solución:* la pregunta de pre-vuelo distingue **datos derivables** (IVA estándar 21%, estructura del asiento) de **datos que deben proporcionarse** (% IRPF, tipo SS empresa, importe de la operación). Dato ambiguo = freno.

---

### Cómo usar este framework

#### Requisitos previos

```bash
# Python 3.10+, se recomienda Conda
conda create -n llm-eval python=3.10
conda activate llm-eval
pip install -r requirements.txt
```

#### Setup

```bash
# 1. Clonar el repo
git clone https://github.com/jleonceo/llm-eval-contable.git
cd llm-eval-contable

# 2. Configurar API key
cp .env.example .env
# Editar .env: ANTHROPIC_API_KEY=tu_clave_aqui

# 3. Añadir tu skill prompt
cp skill_prompt.example.md skill_prompt.md
# Editar skill_prompt.md con tu system prompt real
```

#### Ejecutar el eval

```bash
# Por defecto: Claude Sonnet 4.6
python runner.py

# Modelo explícito
python runner.py --model sonnet
python runner.py --model opus
python runner.py --model haiku

# Evaluar un resultado existente
python grader.py results/2026-05-28_1654_sonnet.json
```

#### Adaptar para tu propia skill

El dataset espera output JSON con esta estructura:

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

Sustituye `skill_prompt.md` por las instrucciones de tu modelo y ajusta `dataset_v2.json` con tus propios casos. La lógica de `grader.py` no depende de la contabilidad, así que sirve para cualquier examen que compare una respuesta con la esperada.

---

### Estructura de ficheros

```
llm-eval-contable/
├── README.md                   ← este fichero
├── dataset_v2.json             ← 50 casos de test con expected outputs
├── grader.py                   ← lógica de evaluación y puntuación
├── runner.py                   ← runner API (carga skill_prompt.md)
├── skill_prompt.md             ← tu system prompt (NO incluido, ver .gitignore)
├── skill_prompt.example.md     ← plantilla con la estructura requerida
├── requirements.txt
├── .env.example
├── .gitignore
└── results/
    └── summary.md              ← progresión de puntuaciones por run
```

---

### Decisiones técnicas clave

**¿Por qué validación por prefijo PGC?**
El PGC usa una jerarquía de cuentas. Las empresas las extienden con sufijos propios (ej. `47200001` para una cuenta IVA específica). Testear códigos exactos haría el eval frágil y específico de empresa. La validación por prefijo (`62x` = cualquier cuenta de gasto) testea el conocimiento contable que realmente importa.

**¿Por qué temperature=0?**
Reproducibilidad. Con temperature > 0, el mismo caso puede pasar o fallar entre runs por razones aleatorias, haciendo imposible atribuir cambios de puntuación a cambios en el prompt. Temperature cero hace cada run determinista.

**¿Por qué output en JSON?**
El output estructurado permite evaluación automática. Las explicaciones contables en texto libre son útiles para humanos pero imposibles de evaluar a escala. El formato JSON además obliga al modelo a ser preciso con los importes.

**¿Por qué un freno obligatorio (PENDIENTE_VERIFICACION)?**
Un asiento incorrecto en un sistema contable es peor que ningún asiento. El patrón freno, rechazar y explicar en lugar de adivinar, es el comportamiento correcto para un asistente contable en producción.

---

### Resultados detallados

Ver [`results/summary.md`](results/summary.md) para el análisis completo con desglose por categoría y análisis de fallos.

---

### Qué pasó después: el capítulo 2

Este proyecto fue el primer paso de algo más grande. El método que ves aquí (examen con respuestas conocidas → medir → corregir la causa raíz → re-examinar todo) escaló después a un **enjambre de 4 agentes** que procesa documentos contables reales de extremo a extremo, con un banco de pruebas de 128 casos generados desde la propia base de datos y puertas de no-regresión.

→ [**accounting-agent-swarm**](https://github.com/jleonceo/accounting-agent-swarm)

---

### Repos relacionados

Este examen es una pieza de un trabajo más amplio: sistemas con varios agentes de IA en los que se puede confiar. Las piezas hermanas, de lo básico a lo avanzado:

- [tu-primer-asistente-ia-web](https://github.com/jleonceo/tu-primer-asistente-ia-web): qué es un asistente de IA y cómo se le instruye, para quien empieza de cero.
- [tesoreria-forecast-ia](https://github.com/jleonceo/tesoreria-forecast-ia): previsión de caja por descomposición con backtesting, más ratios y aging.
- [control-interno-fraude-ia](https://github.com/jleonceo/control-interno-fraude-ia): detección de fraude contable con aritmética, dentro de un marco de control interno.
- [accounting-agent-swarm](https://github.com/jleonceo/accounting-agent-swarm): el enjambre de agentes que creció de este examen, con sus caídas explicadas.
- [orquestacion-enjambres-ia](https://github.com/jleonceo/orquestacion-enjambres-ia): con muchos agentes, cómo se enruta cada petición y se prueba que no rompe al crecer.
- [gobernanza-skills-analiticas](https://github.com/jleonceo/gobernanza-skills-analiticas): gobernar skills con golden sets, puertas de no-regresión y verificador.
- [verificacion-determinista-ia](https://github.com/jleonceo/verificacion-determinista-ia): comprobar la coherencia del estado por pura aritmética, sin IA.
- [agent-memory-governance](https://github.com/jleonceo/agent-memory-governance): que la memoria del agente no acabe siendo un vertedero.

---

### Autor

**Juan Luis León Rodríguez**
Analista de Datos · Business Intelligence · IA Aplicada al Negocio

-  [LinkedIn](https://linkedin.com/in/jlleonrodriguez/)
-  [GitHub](https://github.com/jleonceo)
-  [Portfolio](https://juanluisleon.vercel.app)

---

<a name="english"></a>
## English

### What This Is

An **eval** is an automated exam for a language model: the same cases every time, each with its correct answer written beforehand, and a program that compares what the model answered against what it should have answered. This repo is an eval-driven pipeline to test and iteratively improve an LLM-based accounting assistant. The skill under test generates Spanish double-entry bookkeeping entries (PGC, *Plan General Contable*) from natural language descriptions.

**The core insight:** improving an LLM skill takes measuring failure patterns systematically, fixing the root cause, and verifying that fixes leave the passing cases intact. Writing more instructions is what everyone tries first. It is also what stops working soonest.

### Score Progression

| Run | Score | % | Key change |
|-----|-------|---|------------|
| Run 1, baseline | 33 / 50 | 66% | Initial skill |
| Runs 2-3 | 36-38 / 50 | 72-76% | VAT taxonomy, ISP rules |
| Run 4 | 41 / 50 | 82% | Brake logic, payroll edge cases |
| Run 5 | 44 / 50 | 88% | SaaS exception, 640 vs 641, garnishments |
| **Run 6, final** | **50 / 50** | **100%** | Dataset fixes + passive accruals & reserves transfer (examples F & G) |

*Run 6 executed on 2026-05-28. Full result in [`results/2026-05-28_1654_sonnet.json`](results/2026-05-28_1654_sonnet.json), re-scorable with `grader.py`. Honest caveat: 100% means the skill no longer fails any pattern this 50-case exam covers, not that it is infallible. Growing the exam is how you find new failures.*

**What happened next:** this method later scaled into a 4-agent swarm processing real accounting documents end-to-end → [accounting-agent-swarm](https://github.com/jleonceo/accounting-agent-swarm).

### How It Works

The grader validates each model response against the dataset expected output:
- **Account matching** by PGC prefix (e.g. `472` matches `47200001`), tests accounting knowledge, not code memorisation
- **Balance check**, Σdebit = Σcredit ±€0.01
- **Semantic flags**, exact match on `requiere_periodificacion`, `isp`, `freno_nominas`, `retencion_irpf`
- **Brake pattern**, model must return `PENDIENTE_VERIFICACION` (empty entry) when essential data is missing

### AI Bias Mitigation

Six cognitive biases were addressed through prompt engineering:

| Bias | Fix |
|------|-----|
| **Recency** | Pre-flight question as last instruction before input |
| **Confirmation** | 8-step checklist resets the "produce output" frame |
| **Anchoring** | Explicit rules for cases where the obvious account is wrong |
| **False balance** | Binary decision criteria, no hedging allowed |
| **Sycophancy** | Trap cases (43-46) require refusing user-provided wrong entries |
| **Cherry picking** | Pre-flight distinguishes derivable data from required data |

### Quick Start

```bash
git clone https://github.com/jleonceo/llm-eval-contable.git
cd llm-eval-contable
pip install -r requirements.txt
cp .env.example .env          # add your ANTHROPIC_API_KEY
cp skill_prompt.example.md skill_prompt.md   # add your system prompt
python runner.py
```

### Related repos

This exam is one piece of a larger effort: multi-agent AI systems you can actually trust. The sibling repos, from the basics upward:

- [tu-primer-asistente-ia-web](https://github.com/jleonceo/tu-primer-asistente-ia-web): what an AI assistant is and how you instruct it, for absolute beginners.
- [tesoreria-forecast-ia](https://github.com/jleonceo/tesoreria-forecast-ia): cash-flow forecasting by decomposition with backtesting, plus ratios and aging.
- [control-interno-fraude-ia](https://github.com/jleonceo/control-interno-fraude-ia): accounting fraud detection with arithmetic, inside an internal-control framework.
- [accounting-agent-swarm](https://github.com/jleonceo/accounting-agent-swarm): the agent swarm that grew from this exam, with its drops explained.
- [orquestacion-enjambres-ia](https://github.com/jleonceo/orquestacion-enjambres-ia): with many agents, how each request is routed and how routing is proven to survive growth.
- [gobernanza-skills-analiticas](https://github.com/jleonceo/gobernanza-skills-analiticas): governing skills with golden sets, no-regression gates and a verifier.
- [verificacion-determinista-ia](https://github.com/jleonceo/verificacion-determinista-ia): checking state coherence by pure arithmetic, without AI.
- [agent-memory-governance](https://github.com/jleonceo/agent-memory-governance): keeping the agent's memory from rotting into a junkyard.

---

## Licencia / License

MIT, see [LICENSE](LICENSE).

---

*Construido con Claude Sonnet 4.6 · Mayo 2026 · Built with Claude Sonnet 4.6 · May 2026*
