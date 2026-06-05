# Workflow Guide

This guide covers running the loan-platform-backend locally, testing the Rule Engine, and collaborating across teams using trunk-based development.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Setup](#local-setup)
3. [Running the Project](#running-the-project)
4. [Testing](#testing)
5. [Rule Engine Walkthrough](#rule-engine-walkthrough)
6. [Git Workflow for Multiple Teams](#git-workflow-for-multiple-teams)
7. [Common Tasks](#common-tasks)

---

## Prerequisites

- **Python 3.12+**
- **Docker** and **Docker Compose** (for postgres, redis)
- **Git** (trunk-based workflow)
- **Make** (for convenience shortcuts)
- **pip-tools** (for dependency compilation)

### Install Python and verify version

```bash
python --version  # Must be >= 3.12
```

### Install system dependencies (Linux/Mac)

```bash
# macOS
brew install python@3.12 docker docker-compose

# Ubuntu/Debian
sudo apt-get install python3.12 python3.12-venv python3-pip
```

### On Windows

- Install [Python 3.12](https://www.python.org/downloads/) with "Add Python to PATH"
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Use `python` or `py -3.12` instead of `python3.12`

---

## Local Setup

### 1. Clone and enter the repo

```bash
cd C:/Projects/debtdactory/backend  # Windows
# or
cd ~/projects/debtdactory/backend     # Unix
```

### 2. Create a virtual environment

```bash
# Create .venv in the project root
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate
# On Unix:
source .venv/bin/activate
```

### 3. Compile and install dependencies

```bash
# Compile locked requirements from *.in fragments
make requirements

# Install all pinned deps (base + dev + services)
pip install -r requirements/base.txt -r requirements/dev.txt \
  -r requirements/services/rule_engine.txt \
  -r requirements/services/auth.txt \
  -r requirements/services/domain_logs.txt \
  -r requirements/services/ocr_jobs.txt
```

**Alternative (if make is not available):**

```bash
bash scripts/compile_requirements.sh
pip install -r requirements/base.txt -r requirements/dev.txt \
  -r requirements/services/rule_engine.txt \
  -r requirements/services/auth.txt \
  -r requirements/services/domain_logs.txt \
  -r requirements/services/ocr_jobs.txt
```

### 4. Set up environment variables

```bash
# Copy the example .env
cp .env.example .env

# Edit .env with your settings (optional for local dev)
# For local development, defaults should work:
#   DATABASE_URL=postgresql+asyncpg://app:app@localhost/loan_platform
#   REDIS_URL=redis://localhost:6379
#   ENVIRONMENT=development
```

### 5. Start Docker services

```bash
# Start postgres, redis, and services in the background
docker-compose up -d

# Verify containers are running
docker-compose ps
```

**Expected output:**
```
NAME                COMMAND                  STATUS
api                 "python -m uvicorn..."   Up
postgres            "docker-entrypoint.s..."  Up
redis               "redis-server..."        Up
```

### 6. Run migrations

```bash
# Apply all pending migrations across all service branches
alembic upgrade head

# Verify the schema (optional)
alembic history
```

---

## Running the Project

### Start the development server

```bash
# From the project root with .venv activated
PYTHONPATH=src python -m uvicorn app.main:create_app \
  --factory \
  --host 0.0.0.0 \
  --port 8000 \
  --reload

# Or use the Makefile shortcut (if available)
make run
```

The API will be available at **http://localhost:8000**.

### API Documentation

FastAPI auto-generates interactive docs:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Check health endpoints

```bash
# Liveness check
curl http://localhost:8000/health
# Response: {"status": "ok"}

# Readiness check (includes DB validation)
curl http://localhost:8000/readyz
# Response: {"status": "ok", "checks": {"database": "ok"}}
```

### View logs

The API logs to stdout in JSON format:

```json
{
  "timestamp": "2026-06-02T10:30:45.123Z",
  "level": "INFO",
  "logger": "app.core.middleware",
  "message": "GET /rule-engine/evaluate",
  "request_id": "abc123def456",
  "status_code": 200,
  "duration_ms": 45.2
}
```

---

## Testing

### Run all tests

```bash
# Collect and run all tests, show coverage
pytest

# With verbose output
pytest -v

# Only failed tests
pytest --lf
```

### Run tests for a specific service

```bash
# Rule Engine tests
pytest tests/services/rule_engine/ -v

# Auth service tests
pytest tests/services/auth/ -v

# Domain Logs tests
pytest tests/services/domain_logs/ -v

# OCR Jobs tests
pytest tests/services/ocr_jobs/ -v
```

### Run specific test file or function

```bash
# Single test file
pytest tests/services/rule_engine/unit/test_matrix_parser.py -v

# Single test function
pytest tests/services/rule_engine/unit/test_matrix_parser.py::test_parses_all_rows -v
```

### Coverage report

```bash
# Run with coverage and generate HTML report
pytest --cov=app --cov-report=html

# Open the report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

**CI enforces ≥80% coverage per service; local testing can help catch issues early.**

### Linting and formatting

```bash
# Check all linting rules (ruff)
ruff check src tests

# Auto-fix linting issues
ruff check --fix src tests

# Format code (black)
black --check src tests

# Format and write back
black src tests

# Type checking (mypy)
mypy src
```

**Run all checks together:**

```bash
make lint   # Check
make format # Fix
```

---

## Rule Engine Walkthrough

The Rule Engine evaluates loan applicants against a matrix of bank eligibility rules. Here's how to understand and test it.

### Architecture Overview

```
┌─ Bank_Eligibility_Matrix.xlsx (8 banks, 16 inputs, 2 outputs)
│
├─ MatrixParser (reads .xlsx rows)
│  └─ outputs: list[MatrixRow] with input/output dicts
│
├─ RuleValidator (validates syntax, types, completeness)
│  └─ outputs: list[ValidationError] or clean rows
│
├─ JDMBuilder (assembles GoRules decision table)
│  └─ outputs: zen.ZenEngine JDM artifact
│
└─ Evaluator (runs engine against applicant input)
   └─ outputs: list[EligibilityResult] per eligible bank
```

### The Matrix

Located at `src/app/services/rule_engine/data/Bank_Eligibility_Matrix.xlsx`.

**Columns (16 input constraints → 2 outputs):**

| Input Constraint | Type | Meaning |
|---|---|---|
| CIBIL Score | int | Credit score (e.g., 400–900) |
| PL Write-off | bool | Any unsecured personal loan default? |
| BL Write-off | bool | Any business loan write-off? |
| CC Default | bool | Credit card default in last 6 months? |
| Home Loan Overdraft | bool | Home loan overdraft? |
| Age | int | Applicant age in years |
| Income (Annual) | float | Annual household income |
| Loan Amount Required | float | Requested loan amount |
| Number of Cards | int | Active credit cards |
| Total CC Limit | float | Combined CC limit |
| Avg CC Utilisation % | float | Average utilization (0–100) |
| Unsecured Loans Count | int | Active unsecured loans |
| Previous Default | bool | Any loan default in last 24 months? |
| Co-applicant Income | float | Co-applicant's annual income |
| Employment Status | str | "salaried" / "self-employed" / "unemployed" |
| Loan Tenor Months | int | Requested repayment period |

**Output (one row per eligibility path):**

| Output | Type | Meaning |
|---|---|---|
| Bank Name | str | (e.g., "HDFC Bank", "Axis Bank", "SBI") |
| Eligibility Description | str | "Eligible", "Review Recommended", etc. |

### Input Schema (Pydantic)

```python
# src/app/services/rule_engine/schemas.py :: ApplicantInput
class ApplicantInput(BaseModel):
    cibil_score: int
    pl_write_off: bool
    bl_write_off: bool
    cc_default: bool
    home_loan_overdraft: bool
    age: int
    income_annual: float
    loan_amount_required: float
    number_of_cards: int
    total_cc_limit: float
    avg_cc_utilisation_percent: float
    unsecured_loans_count: int
    previous_default: bool
    co_applicant_income: float
    employment_status: str
    loan_tenor_months: int

    model_config = ConfigDict(json_schema_extra={...})
```

### API Endpoints

#### POST /rule-engine/evaluate

**Request:**

```json
{
  "cibil_score": 750,
  "pl_write_off": false,
  "bl_write_off": false,
  "cc_default": false,
  "home_loan_overdraft": false,
  "age": 35,
  "income_annual": 1200000.0,
  "loan_amount_required": 500000.0,
  "number_of_cards": 2,
  "total_cc_limit": 300000.0,
  "avg_cc_utilisation_percent": 45.0,
  "unsecured_loans_count": 1,
  "previous_default": false,
  "co_applicant_income": 800000.0,
  "employment_status": "salaried",
  "loan_tenor_months": 60
}
```

**Response (200 OK):**

```json
{
  "data": {
    "eligible_banks": [
      {
        "bank_name": "HDFC Bank",
        "description": "Eligible",
        "matched_rule_count": 1
      },
      {
        "bank_name": "SBI",
        "description": "Eligible",
        "matched_rule_count": 2
      }
    ],
    "matched_rule_count": 3
  },
  "error": null
}
```

#### POST /rule-engine/reload

Reloads the matrix from disk and rebuilds the JDM engine (useful during development).

**Request:**

```json
{}
```

**Response (200 OK):**

```json
{
  "data": {
    "status": "reloaded",
    "rows_loaded": 42,
    "jdm_version": "abc123def456"
  },
  "error": null
}
```

### Testing the Rule Engine

#### 1. Unit test: Matrix parsing

```bash
pytest tests/services/rule_engine/unit/test_matrix_parser.py -v
```

Tests that the `.xlsx` parser correctly extracts all rows and maps columns.

**What it checks:**
- Correctly reads all rows (8 banks)
- Maps input columns (16) and output columns (2)
- Handles blank cells as unconstrained
- Detects malformed rows

#### 2. Unit test: Validation

```bash
pytest tests/services/rule_engine/unit/test_rule_validator.py -v
```

Tests that the validator catches errors:
- Unknown column names → error
- Type mismatches (e.g., age: "old" instead of int) → error
- Missing bank_name → error

#### 3. Unit test: JDM building

```bash
pytest tests/services/rule_engine/unit/test_jdm_builder.py -v
```

Tests that the JDM graph is correctly assembled from parsed rows.

#### 4. Unit test: Evaluation

```bash
pytest tests/services/rule_engine/unit/test_evaluator.py -v
```

Tests that the zen-engine correctly evaluates applicants and returns eligible banks.

#### 5. Integration test: API endpoint

```bash
pytest tests/services/rule_engine/integration/test_eligibility_api.py -v
```

Tests the full flow: POST request → parse → validate → evaluate → response.

### Debugging the Engine

#### Enable debug logging

```bash
# Set in .env or inline
RULE_ENGINE_DEBUG=true
python -m uvicorn app.main:create_app --factory --reload
```

#### Inspect the JDM artifact

```python
# In a Python REPL or test
from app.services.rule_engine.engine.evaluator import Evaluator

evaluator = Evaluator(matrix_path="src/app/services/rule_engine/data/Bank_Eligibility_Matrix.xlsx")
print(evaluator.jdm)  # Prints the zen.ZenEngine JDM graph
```

#### Test with sample applicants

```bash
# Use fixtures/applicants.json
python -c "
import json
with open('tests/services/rule_engine/fixtures/applicants.json') as f:
    applicants = json.load(f)
    for name, data in applicants.items():
        print(f'{name}: {data}')
"
```

---

## Git Workflow for Multiple Teams

The monorepo uses **trunk-based development** with per-service isolation to enable multiple teams to work in parallel without blocking each other.

### Key Principles

1. **One main branch:** All work flows through `main` (never `master`, never long-lived feature branches).
2. **Short-lived branches:** Create a branch, make changes, open a PR, merge within 1–3 days.
3. **No cross-service PRs:** Each PR touches one service or shared code (`app/core`, `app/common`).
4. **CI enforces code quality:** All checks must pass before merge (ruff, black, mypy, pytest, coverage).
5. **Conventional commits:** All commits use a standard format for clarity and changelog generation.

### Branch Naming

Create branches with this pattern:

```
<team>/<service>/<description>
feat/<service>/<description>
fix/<service>/<description>
chore/<team>/<description>
docs/<description>
```

**Examples:**

```bash
# Feature branch for rule-engine team
git checkout -b feat/rule-engine/zen-engine-integration

# Bug fix for auth service
git checkout -b fix/auth/jwt-expiry-handling

# Chore for platform team
git checkout -b chore/platform/upgrade-fastapi

# Documentation update
git checkout -b docs/architecture-diagram
```

### Workflow Steps

#### 1. Sync with main

```bash
# Always start from the latest main
git fetch origin
git checkout main
git pull origin main
```

#### 2. Create a feature branch

```bash
git checkout -b feat/rule-engine/matrix-parser

# Or in one go:
git switch -c feat/rule-engine/matrix-parser
```

#### 3. Make changes

Edit files in your service directory. **Do not touch:**

- `src/app/core/` (unless coordinating with platform team)
- `src/app/common/` (unless coordinating with platform team)
- `src/app/main.py` (auto-discovery; no registration needed)
- `src/app/api/router_registry.py` (same)
- `pyproject.toml` (unless adding a new dependency globally)

**Your changes should be isolated to:**

```
src/app/services/<your-service>/
  ├── router.py         ← Update endpoint logic
  ├── service.py        ← Update business logic
  ├── schemas.py        ← Add/update request/response DTOs
  ├── models.py         ← Add/update ORM models
  ├── config.py         ← Add/update settings
  ├── constants.py      ← Add/update constants
  ├── exceptions.py     ← Add/update exceptions
  ├── dependencies.py   ← Add/update DI functions
  └── ...other modules
```

#### 4. Write and run tests

```bash
# Add tests in tests/services/<your-service>/
mkdir -p tests/services/rule-engine/unit
echo "def test_something(): pass" > tests/services/rule-engine/unit/test_new.py

# Run your service's tests
pytest tests/services/rule-engine/ -v

# Check coverage
pytest tests/services/rule-engine/ --cov=app.services.rule-engine --cov-report=term-missing
```

#### 5. Lint and format

```bash
# Format code
black src/app/services/rule-engine tests/services/rule-engine

# Check all rules
ruff check --fix src/app/services/rule-engine tests/services/rule-engine

# Type check
mypy src/app/services/rule-engine
```

#### 6. Commit with conventional commits

Conventional Commits format:

```
<type>(<scope>): <subject>

<body (optional)>

<footer (optional)>
```

**Types:** `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `ci`

**Scopes:** `rule-engine`, `auth`, `domain-logs`, `ocr-jobs`, `core`, `common`, `ci`

**Examples:**

```bash
# Feature
git commit -m "feat(rule-engine): implement zen-engine integration

Integrate GoRules zen-engine to evaluate applicants against the bank matrix.

Closes #42"

# Bug fix
git commit -m "fix(auth): correct JWT expiry validation"

# Refactoring
git commit -m "refactor(rule-engine): extract rule validation to separate module

Improves testability and readability."

# Test
git commit -m "test(rule-engine): add tests for matrix parser"

# Docs
git commit -m "docs: update architecture decision record"

# Chore (dependencies, config, tooling)
git commit -m "chore(deps): upgrade FastAPI to 0.104.0"
```

**Avoid:**

```bash
# ❌ No subject line
git commit -m "fixes"

# ❌ No scope
git commit -m "feat: added stuff"

# ❌ Wrong format
git commit -m "FEATURE: something"
```

#### 7. Push and open a pull request

```bash
# Push to origin
git push -u origin feat/rule-engine/matrix-parser

# Open a PR via GitHub CLI (or web UI)
gh pr create \
  --title "feat(rule-engine): implement zen-engine integration" \
  --body "Integrates GoRules zen-engine to evaluate applicants against the bank eligibility matrix." \
  --draft  # Mark as draft until ready for review
```

**PR title and body:**

- **Title:** One-liner matching your conventional commit message.
- **Body:** Explain *why* (context, problem solved), *what* (changes), and any *testing* done.

**Example:**

```markdown
## Summary

Implement zen-engine integration to evaluate applicants against the bank eligibility matrix.

- Parses Bank_Eligibility_Matrix.xlsx
- Validates input constraints
- Builds GoRules decision table
- Evaluates applicants → list of eligible banks

## Testing

- [x] Unit tests for parser, validator, JDM builder, evaluator
- [x] Integration test for POST /rule-engine/evaluate endpoint
- [x] Manual curl test with sample applicant data

## Checklist

- [x] Code follows project style (ruff, black, mypy)
- [x] Tests pass locally (pytest)
- [x] Coverage ≥80% for rule-engine service
- [x] Commits use conventional format
```

#### 8. CI runs automatically

When you push, GitHub Actions runs:

1. **Ruff:** Linting
2. **Black:** Code format check
3. **Mypy:** Type checking
4. **Pytest:** Unit + integration tests
5. **Coverage:** Per-service gate (≥80%)

Only if **all checks pass** can the PR be merged.

**Monitor your PR:**

```bash
# Check CI status from the command line
gh pr checks <pr-number>

# Watch PR status
gh pr view <pr-number>
```

#### 9. Request review

Tag reviewers (usually your service team and the platform team for shared code):

```bash
# Via GitHub CLI
gh pr edit <pr-number> --add-reviewer @alice @bob

# Or via web UI: click "Reviewers" → select team members
```

#### 10. Address feedback

Reviewers may request changes. Address them:

```bash
# Edit files to fix issues
# Commit and push (do not force-push or rewrite history)
git add .
git commit -m "refactor(rule-engine): improve error messages based on review feedback"
git push origin feat/rule-engine/matrix-parser

# CI re-runs automatically; once all checks pass, reviewers can approve
```

#### 11. Merge to main

Once approved and CI passes:

```bash
# Squash and merge (to keep history clean)
gh pr merge <pr-number> --squash

# Or use the web UI: "Squash and merge"
```

**After merge:**

```bash
# Return to main
git checkout main
git pull origin main

# Delete local branch
git branch -d feat/rule-engine/matrix-parser

# Delete remote branch (GitHub does this automatically on merge)
git push origin --delete feat/rule-engine/matrix-parser
```

### Handling Conflicts

If `main` has advanced and your branch is out of date:

```bash
# Fetch latest main
git fetch origin

# Rebase your branch on top of origin/main (keeps history linear)
git rebase origin/main

# If conflicts occur, resolve them in your editor, then:
git add .
git rebase --continue

# Force-push to your PR branch (safe because it's your own branch)
git push origin feat/rule-engine/matrix-parser --force-with-lease
```

**Avoid merging main into your branch** — rebasing keeps the history clean for a monorepo.

### Service Teams and Ownership

Each service is owned by a team (defined in `.github/CODEOWNERS`):

```
# .github/CODEOWNERS

src/app/services/rule-engine/ @platform/rule-engine-team
src/app/services/auth/ @platform/auth-team
src/app/services/domain-logs/ @platform/domain-logs-team
src/app/services/ocr-jobs/ @platform/ocr-team

src/app/core/ @platform/platform-team
src/app/common/ @platform/platform-team
src/app/api/ @platform/platform-team
```

**GitHub enforces code ownership:** PRs touching owned paths automatically request reviews from the owning team.

### Avoiding Cross-Service Dependencies

**The monorepo rule:** Services depend on `core/common` only, never on each other.

**If you need to share logic:**

1. **Move to `app/common/`:** Utility functions, base classes, shared schemas.
2. **Document the shared interface:** Add docstrings and tests.
3. **Coordinate with platform team:** Ensure the shared API doesn't couple services.

**Example:** If `auth` and `ocr_jobs` both need JWT validation, extract it to:

```python
# src/app/common/security/jwt.py
def decode_and_validate_jwt(token: str) -> dict[str, Any]:
    ...

# Then both services import:
from app.common.security.jwt import decode_and_validate_jwt
```

---

## Common Tasks

### Adding a new service

Follow `docs/service_template.md` — it shows how to scaffold a new service without editing any shared files.

### Updating a shared dependency

Edit the corresponding `.in` file and recompile:

```bash
# Edit requirements/base.in (for all services)
# or requirements/dev.in (for dev tools)

# Recompile and reinstall
make requirements
pip install -r requirements/base.txt -r requirements/dev.txt ...
```

### Running migrations

```bash
# Generate a new migration for a service
alembic revision --autogenerate -m "rule-engine: add evaluation_audit table"

# Specify the branch label
# (The migration file will be in migrations/versions/rule-engine/)

# Run all pending migrations
alembic upgrade head

# Rollback one revision
alembic downgrade -1
```

### Deploying to production

```bash
# Build the production image
docker build -f docker/api/Dockerfile -t loan-platform-api:latest .

# Tag it
docker tag loan-platform-api:latest <registry>/loan-platform-api:v0.1.0

# Push to registry
docker push <registry>/loan-platform-api:v0.1.0

# Deploy with prod compose (no mounts, 4 workers, healthchecks)
docker-compose -f compose.yaml -f compose.prod.yaml up -d
```

### Accessing logs

```bash
# Stream API logs
docker-compose logs -f api

# Stream postgres logs
docker-compose logs -f postgres

# Stream redis logs
docker-compose logs -f redis
```

### Resetting the database

```bash
# Drop and recreate the database
docker-compose exec postgres dropdb -U app loan_platform
docker-compose exec postgres createdb -U app loan_platform

# Re-run migrations
alembic upgrade head
```

---

## Summary

| Task | Command |
|---|---|
| **Setup** | `python -m venv .venv && source .venv/bin/activate && make requirements && docker-compose up -d && alembic upgrade head` |
| **Run API** | `uvicorn app.main:create_app --factory --reload` |
| **Run tests** | `pytest tests/services/<service>/ -v` |
| **Check code** | `ruff check src && black --check src && mypy src` |
| **Fix code** | `black src && ruff check --fix src` |
| **Create branch** | `git switch -c feat/<service>/<desc>` |
| **Commit** | `git commit -m "feat(<service>): description"` |
| **Push & PR** | `git push -u origin feat/<service>/<desc> && gh pr create` |

---

## Questions?

- **Architecture:** See `docs/architecture.md`
- **Service template:** See `docs/service_template.md`
- **Git decisions:** See `docs/git_workflow.md` and `.github/CODEOWNERS`
- **Rule Engine:** See `src/app/services/rule_engine/README.md`
