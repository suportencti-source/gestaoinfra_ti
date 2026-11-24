# Context: Python/Flask App

## Commands
- Run: `flask run` | `python app.py`
- Test: `pytest -v`
- Lint/Format: `ruff check .` | `ruff format .`

## Guidelines
- Style: PEP 8, modular Flask Blueprints, SQLAlchemy ORM.
- Config: Use `os.environ` / `.env` (no hardcoded secrets).
- Errors: Clean try/except, standard JSON responses for APIs.

---

## Modes

### 1. Feature (Criar Funcionalidade)
- Write modular, clean code following existing architecture.
- Add corresponding unit/integration tests with `pytest`.
- Do not break existing features; add docstrings to complex functions.

### 2. Optimize (Revisar e Otimizar Flask)
- **Focus:** Performance, security (OWASP), and queries.
- **Checks:** Detect N+1 queries (`joinedload`/`subqueryload`), missing pagination, and insecure inputs.
- **Output:** Show original snippet, explain issue, provide optimized code.

### 3. Review (Code Review & Opiniões)
- Categorize feedback: **Critial** (bugs), **Improvement** (readability/PEP 8), **Suggestion** (Pythonic alternatives).
- Keep explanations concise, focusing on the "why".