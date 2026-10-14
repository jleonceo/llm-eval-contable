English version: [README.en.md](README.en.md)

# Examen automático para una IA contable

Un examen de 50 casos con su respuesta correcta y un corrector en Python que puntúan a un modelo de lenguaje
cuando propone asientos contables según el Plan General Contable. Sirve para mejorar las instrucciones del modelo
midiendo, versión a versión, qué casos acierta y cuáles falla.

**Resultado:** en seis versiones de las instrucciones, el modelo pasó de acertar 33 de los 50 casos (66 %) a
acertarlos todos. En julio se descubrió que dos casos del examen enseñaban un tratamiento fiscal equivocado. Con
el examen corregido, aquellas respuestas acertarían 48 de 50.

```bash
pip install -r requirements.txt
python grader.py results/2026-05-28_1654_sonnet.json
```

El corrector vuelve a puntuar la última ejecución guardada sin llamar a la API. Para ejecutar el examen entero
hace falta una clave de la API de Anthropic y unas instrucciones propias (ver «Cómo se usa»).

## El problema de partida

Un modelo de lenguaje propone un asiento con la misma seguridad tanto si acierta como si no. Para saber si un
cambio en sus instrucciones lo mejora hace falta un examen fijo, con la respuesta correcta escrita antes, que se
repita entero después de cada cambio. Así se ve también si el arreglo de un caso ha estropeado otro.

## Qué hay dentro

1. `dataset_v2.json` contiene 50 casos sintéticos en 12 categorías: facturas emitidas y recibidas,
   operaciones intracomunitarias, inversión del sujeto pasivo, nóminas, embargos, amortizaciones,
   periodificaciones, cierre, impuestos, leasing y renting, y casos trampa.
2. `runner.py` pasa cada caso al modelo, con temperatura 0, y guarda la respuesta tal cual.
3. `grader.py` compara cada respuesta con la correcta: el estado (registrar o pedir más datos), el cuadre,
   cada línea por cuenta, importe y lado, y cuatro marcas como la retención de IRPF o la periodificación.
4. `results/` guarda la ejecución del 28/05/2026 y la evolución de las seis versiones.
5. `skill_prompt.example.md` es la plantilla de las instrucciones del modelo.

El corrector acepta la cuenta por su grupo del Plan General Contable: si la respuesta correcta es la 4300 y el
modelo escribe la 43000002, la da por buena, porque las dos son clientes.

## Lo que sale

| Versión | Aciertos | Cambio principal en las instrucciones |
|---|---|---|
| 1 | 33 de 50 | Instrucciones iniciales |
| 2 y 3 | 36 y 38 | Tipos de IVA, reglas de inversión del sujeto pasivo y cuándo parar a pedir datos |
| 4 | 41 | Alta del leasing en el activo y periodificaciones |
| 5 | 44 | Suscripciones de software como gasto, sueldos frente a indemnizaciones y embargos |
| 6 | 50 | Periodificación de ingresos, traspaso a reservas y correcciones del examen |

Los cambios que más ayudaron atacan errores de razonamiento conocidos.

Una pregunta final obliga al modelo a
comprobar si faltan datos, como el porcentaje de IRPF, antes de escribir el asiento. Cuatro casos trampa le piden
un asiento descuadrado o sin datos suficientes, y la respuesta correcta es negarse y pedir lo que falta.

## Límites

- El examen se corrigió el 20/07/2026. El caso 21 trataba el alquiler de un local como inversión del sujeto
  pasivo, cuando lleva IVA repercutido y retención del 19 % de IRPF. El caso 20 llamaba rehabilitación a una
  reforma de 5.000 € y además dictaba la respuesta en el propio enunciado. Los dos se reescribieron.
- El 48 de 50 sale de puntuar las respuestas de mayo con el examen corregido, pero los enunciados de esos dos
  casos también cambiaron. La cifra vigente solo se sabrá repitiendo la ejecución.
- `grader.py` puntúa contra la respuesta correcta guardada dentro del resultado, la de mayo. Por eso, ejecutado
  sobre el fichero de `results/`, sigue dando 50 de 50.
- Aprobar este examen no hace infalible al modelo: solo dice que ya no falla los casos que el examen cubre.
- Las instrucciones evaluadas no se publican; el repositorio trae una plantilla.

## Cómo se usa

```bash
cp .env.example .env                          # poner ANTHROPIC_API_KEY
cp skill_prompt.example.md skill_prompt.md    # escribir las instrucciones propias
python runner.py --model sonnet               # también opus o haiku
python grader.py results/<fichero>.json
```

Para otro dominio basta con cambiar `dataset_v2.json` y las instrucciones: el corrector compara una respuesta en
JSON con la esperada y no depende de la contabilidad.

## Repositorios relacionados

- [accounting-agent-swarm](https://github.com/jleonceo/accounting-agent-swarm): el paso siguiente, cuatro agentes
  que procesan documentos contables reales, medidos con un examen de 128 casos.
- [gobernanza-skills-analiticas](https://github.com/jleonceo/gobernanza-skills-analiticas): las reglas para
  cambiar las instrucciones de un modelo sin empeorar lo que ya funcionaba.
- [analisis-contable](https://github.com/jleonceo/analisis-contable): cuenta de resultados y tesorería de 2024
  con pandas, comprobadas por un segundo camino.

---

*Parte del portfolio de [Juan Luis León](https://github.com/jleonceo) · [juanluisleon.vercel.app](https://juanluisleon.vercel.app) · Licencia [MIT](LICENSE)*
