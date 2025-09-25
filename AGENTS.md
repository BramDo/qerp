# Repository Guidelines

## Project Structure & Module Organization
`src/` holds production code and is split by domain: `dmet` (embedding diagnostics), `ham` (mapping to qubits), `solvers` (SKQD/ADAPT-VQE), `mitigation` (error mitigation), `neb` (DFT/NEB pipeline), `post` (analysis), and `utils` (IO/config). Keep experiments in `notebooks/` (A = toy fragment, B = benzothiofeen path). Reference data lives in `data/`, while `reports/` captures writeups and figures. Leave bulky raw exports outside Git.

## Build, Test, and Development Commands
Set up a virtual environment and install dependencies with `python -m venv .venv && source .venv/bin/activate && python -m pip install -r requirements.txt`. Use `python -m pip install -e .` when iterating on modules. Run notebooks through `jupyter lab notebooks/A_toy_fragment_SKQD.ipynb` once Aer GPU support is configured. New scripts should be exposed via `python -m qerp.<module>` to stay aligned with the package layout.

## Coding Style & Naming Conventions
Adhere to PEP 8, four-space indentation, and lines under 100 characters. Keep public APIs type-hinted and prefer descriptive snake_case names (e.g. `build_active_space`). Constants go in upper snake case, and module docstrings should explain chemistry context when non-obvious. Strip notebook outputs before committing and leave `.ipynb_checkpoints` ignored. No formatter is enforced; coordinate before adding tooling configs.

## Testing Guidelines
Mirror the module tree under `tests/` (for example, `tests/solvers/test_skqd.py`) and drive tests with `pytest`. Use `qiskit.providers.fake` backends or lightweight Hamiltonians to avoid hardware dependencies. Cover DMET selection logic, solver convergence heuristics, and mitigation fallbacks. Run `pytest -q` locally and annotate any stochastic tolerances or skipped cases in the pull request.

## Commit & Pull Request Guidelines
Follow the `<scope>: <imperative summary>` convention from `init: QERP skeleton` and keep commits focused. Commit bodies should record chemistry or numerical rationale when it affects reproducibility. Pull requests need a short problem statement, resulting energy or mitigation deltas, linked issues, and the tests executed (`pytest`, notebooks run, backend type). Request review from the module owner and call out follow-up tasks.

## Security & Configuration Tips
Store IBM Quantum or other provider credentials in environment variables or a keyring, loading them via `os.getenv`. Scrub proprietary geometries before uploading to `data/` and avoid committing oversized raw outputs. When sharing notebooks, strip metadata that might reveal hardware or credential details.
