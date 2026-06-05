# Team Onboarding Checklist

Use this checklist when your team joins the loan-platform-backend project. Follow it **once per team**, then individual contributors use the workflow in [`docs/workflow.md`](docs/workflow.md).

## Phase 1: Environment Setup (15 minutes)

This is done **once per developer machine**. After this, jumping between services is just `git checkout -b feat/<service>/<desc>`.

- [ ] **Clone the repo**
  ```bash
  cd ~/projects && git clone <repo-url> debtdactory/backend && cd debtdactory/backend
  ```

- [ ] **Verify Python version**
  ```bash
  python --version  # Must be 3.12.x
  ```

- [ ] **Create virtual environment**
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # Windows: .venv\Scripts\activate
  ```

- [ ] **Compile and install dependencies**
  ```bash
  make requirements
  pip install -r requirements/base.txt -r requirements/dev.txt \
    -r requirements/services/rule_engine.txt \
    -r requirements/services/auth.txt \
    -r requirements/services/domain_logs.txt \
    -r requirements/services/ocr_jobs.txt
  ```

- [ ] **Start Docker services**
  ```bash
  docker-compose up -d
  ```

- [ ] **Verify setup**
  ```bash
  alembic upgrade head
  PYTHONPATH=src python -c "import app.main"  # Should print 15 routes
  ```

- [ ] **Start the API and open docs**
  ```bash
  python -m uvicorn app.main:create_app --factory --reload
  # Visit http://localhost:8000/docs
  ```

---

## Phase 2: Service Kickoff (1 hour)

This is done **once per team** to familiarize with the service's codebase and testing.

### For the Rule Engine team

- [ ] **Read the service contract**
  ```bash
  open src/app/services/rule_engine/README.md
  ```

- [ ] **Understand the matrix**
  ```bash
  open src/app/services/rule_engine/data/Bank_Eligibility_Matrix.xlsx
  ```

- [ ] **Understand the pipeline (in order)**
  1. `matrix_parser.py` — reads `.xlsx` into rows
  2. `rule_validator.py` — validates input/output columns
  3. `jdm_builder.py` — builds zen-engine decision table
  4. `evaluator.py` — runs engine against applicants

- [ ] **Run the Rule Engine tests**
  ```bash
  pytest tests/services/rule_engine/ -v
  ```

- [ ] **Test the endpoint manually**
  ```bash
  curl -X POST http://localhost:8000/rule-engine/evaluate \
    -H "Content-Type: application/json" \
    -d @tests/services/rule_engine/fixtures/sample_request.json
  ```

- [ ] **Read the implementation guide**
  ```bash
  open docs/workflow.md#rule-engine-walkthrough
  ```

### For the Auth team

- [ ] **Read the service contract**
  ```bash
  open src/app/services/auth/README.md
  ```

- [ ] **Understand the channels** (in `src/app/services/auth/channels/`)
  - `base.py` — protocol defining all auth methods
  - `email_password.py` — username/password login
  - `otp_sms.py` — OTP via SMS
  - `oauth_google.py` — OAuth via Google
  - `magic_link.py` — Passwordless magic link

- [ ] **Review token handling** (in `src/app/services/auth/tokens/`)
  - `jwt.py` — JWT encoding/decoding
  - `refresh.py` — Refresh token lifecycle

- [ ] **Run the Auth tests**
  ```bash
  pytest tests/services/auth/ -v
  ```

### For the Domain Logs team

- [ ] **Read the service contract**
  ```bash
  open src/app/services/domain_logs/README.md
  ```

- [ ] **Understand streaming** (in `src/app/services/domain_logs/streaming/`)
  - `sse.py` — Server-Sent Events implementation
  - `websocket.py` — WebSocket implementation
  - `tailer.py` — Log file tailing

- [ ] **Run the Domain Logs tests**
  ```bash
  pytest tests/services/domain_logs/ -v
  ```

### For the OCR Jobs team

- [ ] **Read the service contract**
  ```bash
  open src/app/services/ocr_jobs/README.md
  ```

- [ ] **Understand async jobs** (in `src/app/services/ocr_jobs/workers/`)
  - `celery_app.py` — Celery app factory (Redis broker)
  - `tasks.py` — `run_ocr` task definition

- [ ] **Understand storage** (in `src/app/services/ocr_jobs/storage/`)
  - `base.py` — Abstract storage interface

- [ ] **Run the OCR Jobs tests**
  ```bash
  pytest tests/services/ocr_jobs/ -v
  ```

---

## Phase 3: Git Workflow Training (30 minutes)

All team members should read this section and understand the workflow before making changes.

- [ ] **Read the git workflow guide**
  ```bash
  open docs/git_workflow.md
  ```

- [ ] **Understand trunk-based development**
  - One `main` branch (no long-lived `dev`, `staging`, etc.)
  - Short-lived branches (1–3 days max)
  - Every PR triggers CI; must pass before merge

- [ ] **Understand branch naming**
  ```
  feat/<service>/<description>   # New feature
  fix/<service>/<description>    # Bug fix
  chore/<team>/<description>     # Config/tooling
  docs/<description>             # Documentation
  ```

- [ ] **Understand conventional commits**
  ```
  feat(rule-engine): implement zen-engine integration
  fix(auth): correct JWT expiry validation
  test(rule-engine): add tests for matrix parser
  docs: update workflow guide
  ```

- [ ] **Create your first branch** (practice)
  ```bash
  git switch -c feat/rule-engine/my-first-feature
  echo "# test" > test.md
  git add test.md
  git commit -m "test(rule-engine): test conventional commits"
  git push -u origin feat/rule-engine/my-first-feature
  # Don't open a PR; just verify the branch exists on GitHub
  # Then delete it:
  git switch main
  git branch -D feat/rule-engine/my-first-feature
  git push origin --delete feat/rule-engine/my-first-feature
  ```

- [ ] **Understand code ownership**
  ```bash
  open .github/CODEOWNERS  # Your service's team is listed
  ```

---

## Phase 4: Making Your First PR (2 hours)

Now you're ready to contribute. Follow this workflow for every change.

- [ ] **Pick a TODO task from your service**
  ```bash
  grep -r "TODO(<your-service>)" src/app/services/<your-service>/
  # Pick one and implement it
  ```

- [ ] **Create a feature branch**
  ```bash
  git switch main && git pull origin main
  git switch -c feat/<service>/<ticket-slug>
  ```

- [ ] **Make your changes**
  - Edit files in `src/app/services/<service>/`
  - Add tests in `tests/services/<service>/`
  - Update docstrings and README.md as needed

- [ ] **Run tests and checks locally**
  ```bash
  # Your service tests
  pytest tests/services/<service>/ -v
  
  # Linting & formatting
  black src/app/services/<service>
  ruff check --fix src/app/services/<service>
  mypy src/app/services/<service>
  
  # Check coverage
  pytest tests/services/<service>/ --cov=app.services.<service> --cov-report=term-missing
  ```

- [ ] **Commit with a conventional message**
  ```bash
  git add .
  git commit -m "feat(<service>): your feature description"
  ```

- [ ] **Push and open a PR**
  ```bash
  git push -u origin feat/<service>/<ticket-slug>
  gh pr create --title "feat(<service>): description" --draft  # Or use GitHub web UI
  ```

- [ ] **Monitor CI and address feedback**
  ```bash
  # Check PR status
  gh pr checks <pr-number>
  
  # If checks fail, fix issues and push again (don't force-push)
  git add .
  git commit -m "fix: address review feedback"
  git push origin feat/<service>/<ticket-slug>
  ```

- [ ] **Merge when ready**
  ```bash
  # After all checks pass and reviewers approve:
  gh pr merge <pr-number> --squash
  
  # Then clean up locally
  git switch main && git pull origin main
  git branch -D feat/<service>/<ticket-slug>
  ```

---

## Phase 5: Daily Development (ongoing)

- [ ] **Every morning, sync with main**
  ```bash
  git fetch origin && git rebase origin/main
  ```

- [ ] **Run full test suite before submitting PR**
  ```bash
  pytest  # All tests
  make check  # Linting + type + test (what CI runs)
  ```

- [ ] **Ask for help in team Slack channel**
  - Tag `@<service>-team` or `@platform-team` with questions
  - Link to the relevant `.md` file when asking about architecture

- [ ] **Use `docs/workflow.md` as your reference**
  - Section: "Common Tasks" covers adding services, updating deps, migrations
  - Section: "Rule Engine Walkthrough" covers testing the engine
  - Section: "Git Workflow for Multiple Teams" covers all git patterns

---

## Troubleshooting

### "I have merge conflicts"

See [`docs/workflow.md#handling-conflicts`](docs/workflow.md#handling-conflicts).

```bash
git fetch origin && git rebase origin/main
# Resolve conflicts in your editor
git add .
git rebase --continue
```

### "My tests are failing"

```bash
# Run just your service tests
pytest tests/services/<your-service>/ -v

# Check the error message; if it's type-related:
mypy src/app/services/<your-service>

# If it's formatting:
black --check src/app/services/<your-service>
```

### "CI is failing but tests pass locally"

Check that:
1. You're on Python 3.12: `python --version`
2. You've installed all deps: `pip install -r requirements/base.txt -r requirements/dev.txt -r requirements/services/<service>.txt`
3. You've run `make check` to simulate CI: `ruff check && black --check && mypy && pytest`

### "I can't import app.main"

Make sure `PYTHONPATH=src`:

```bash
export PYTHONPATH=src  # Unix
set PYTHONPATH=src     # Windows CMD
$env:PYTHONPATH="src"  # Windows PowerShell

PYTHONPATH=src python -c "import app.main"
```

### "Docker containers won't start"

```bash
# Stop and remove old containers
docker-compose down -v

# Rebuild images
docker-compose up -d --build

# Check logs
docker-compose logs postgres
docker-compose logs redis
```

---

## Resources

| Resource | Purpose |
|---|---|
| [`docs/workflow.md`](docs/workflow.md) | **Start here.** Complete setup, testing, Rule Engine, git for teams. |
| [`docs/architecture.md`](docs/architecture.md) | Why the monolith is structured this way; request lifecycle. |
| [`docs/git_workflow.md`](docs/git_workflow.md) | Git patterns (branches, commits, conflicts, rebasing). |
| [`docs/service_template.md`](docs/service_template.md) | How to add a new service without editing shared files. |
| [`docs/adr/0001-modular-monolith.md`](docs/adr/0001-modular-monolith.md) | Architectural Decision Record; the "why" behind all decisions. |
| `src/app/services/<service>/README.md` | Your service's contract (inputs, outputs, pipeline). |
| `.github/CODEOWNERS` | Who owns what code. Your team is listed here. |

---

## Questions?

- **Slack:** Tag `@platform-team` or `@<service>-team`
- **GitHub Issues:** Create an issue with `[docs]` tag if something in this guide is unclear
- **Office Hours:** Platform team hosts async office hours (check team calendar)

Welcome to the team! 🚀
