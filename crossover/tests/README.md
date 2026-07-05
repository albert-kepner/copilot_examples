# Tests Overview

This folder contains pytest suites for the customer record clustering logic.

## Test Suites

- `test_simple_cases.py`
  - First-pass coverage with readable, small scenarios.
  - Focuses on one or two business units and up to five records.

- `test_complex_cases.py`
  - Second-pass coverage with richer merge/invariant scenarios.
  - Includes transitive merges, survivor behavior, and index repoint checks.

## Output Style

Both suites print, for each case:

- Intended outcome
- Input records
- Resulting cluster(s)
- Identifier sets (`npi`, `ncpdp`, `dea`)
- `customer_record_counts`

Use `-s` with pytest to see this printed output.

## Run Commands

```powershell
cd C:\_C\copilot_examples\crossover
pytest -q -s tests\test_simple_cases.py
pytest -q -s tests\test_complex_cases.py
pytest -q -s tests
```

## Notes

- `tests\conftest.py` ensures top-level imports like `cluster` and `cluster_state` resolve during test runs.
- If you only want pass/fail summaries without printed case details, omit `-s`.

