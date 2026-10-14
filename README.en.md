Versión en español: [README.md](README.md)

# Automated test for an accounting AI

A 50-case test set with correct answers and a Python grader that score a language model when it proposes
accounting entries under the Spanish chart of accounts. It is used to improve the model's instructions by
measuring, version after version, which cases it gets right and which it fails.

**Result:** over six versions of the instructions, the model went from getting 33 of the 50 cases right (66 %) to
getting all of them right. In July two cases in the test turned out to teach a wrong tax treatment. With the
corrected test, those answers would score 48 out of 50.

```bash
pip install -r requirements.txt
python grader.py results/2026-05-28_1654_sonnet.json
```

The grader re-scores the last saved run without calling the API. Running the whole test needs an Anthropic API
key and your own instructions (see «How to use it»).

## The starting problem

A language model proposes an entry with the same confidence whether it is right or not. To know whether a change
to its instructions improves it, you need a fixed test, with the correct answer written beforehand, repeated in
full after every change. That also shows whether fixing one case broke another.

## What is inside

1. `dataset_v2.json` holds 50 synthetic cases in 12 categories: issued and received invoices, intra-EU
   operations, reverse charge, payroll, garnishments, depreciation, accruals, year-end close, taxes, leasing and
   renting, and trap cases.
2. `runner.py` sends each case to the model, at temperature 0, and saves the answer as it comes.
3. `grader.py` compares each answer with the correct one: the status (record or ask for more data), the balance,
   each line by account, amount and side, and four flags such as income-tax withholding or accruals.
4. `results/` keeps the 28/05/2026 run and the progress over the six versions.
5. `skill_prompt.example.md` is the template for the model's instructions.

The grader accepts an account by its group in the chart of accounts: if the correct answer is 4300 and the model
writes 43000002, it counts as right, because both are customers.

## What comes out

| Version | Correct | Main change to the instructions |
|---|---|---|
| 1 | 33 of 50 | Initial instructions |
| 2 and 3 | 36 and 38 | VAT rates, reverse-charge rules and when to stop and ask for data |
| 4 | 41 | Recognising the lease as an asset, and accruals |
| 5 | 44 | Software subscriptions as expenses, wages versus severance, and garnishments |
| 6 | 50 | Deferred income, transfer to reserves and fixes to the test |

The changes that helped most target known reasoning errors.

A final question makes the model check whether data
is missing, such as the income-tax withholding rate, before writing the entry. Four trap cases ask it for an
unbalanced entry or one without enough data, and the right answer is to refuse and ask for what is missing.

## Limits

- The test was corrected on 20/07/2026. Case 21 treated the rent of business premises as reverse charge, when it
  carries output VAT and a 19 % income-tax withholding. Case 20 called a 5,000 € refurbishment a rehabilitation
  and also dictated the answer in the question itself. Both were rewritten.
- The 48 out of 50 comes from scoring the May answers against the corrected test, but the questions of those two
  cases also changed. The current figure will only be known by running the test again.
- `grader.py` scores against the correct answer saved inside the result, the May one. That is why, run on the file
  in `results/`, it still gives 50 out of 50.
- Passing this test does not make the model infallible: it only says it no longer fails the cases the test
  covers.
- The instructions that were evaluated are not published; the repository includes a template.

## How to use it

```bash
cp .env.example .env                          # set ANTHROPIC_API_KEY
cp skill_prompt.example.md skill_prompt.md    # write your own instructions
python runner.py --model sonnet               # also opus or haiku
python grader.py results/<file>.json
```

For another domain, change `dataset_v2.json` and the instructions: the grader compares a JSON answer with the
expected one and does not depend on accounting.

## Related repositories

- [accounting-agent-swarm](https://github.com/jleonceo/accounting-agent-swarm): the next step, four agents that
  process real accounting documents, measured with a 128-case test.
- [gobernanza-skills-analiticas](https://github.com/jleonceo/gobernanza-skills-analiticas): the rules for
  changing a model's instructions without breaking what already worked.
- [analisis-contable](https://github.com/jleonceo/analisis-contable): 2024 income statement and cash with
  pandas, checked by a second route.

---

*Part of [Juan Luis León](https://github.com/jleonceo)'s portfolio · [juanluisleon.vercel.app](https://juanluisleon.vercel.app) · Licence [MIT](LICENSE)*
