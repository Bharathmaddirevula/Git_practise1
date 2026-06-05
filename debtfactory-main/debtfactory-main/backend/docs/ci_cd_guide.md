# Git + CI/CD Guide (for the team)

How we use Git, GitHub Actions CI, and CD on this repo. Read this once; keep the
[Quick reference](#quick-reference) handy.

```
 your branch ──push──▶ Pull Request ──▶ CI (green required) ──▶ review ──▶ squash-merge to main ──▶ CD
```

---

## 0. One-time: put the project on GitHub

> The repo isn't initialised yet. A maintainer does this **once**.

```bash
cd debtdactory/backend
git init -b main
git add .
git commit -m "chore: initial import"

# create the remote (GitHub CLI), then push
gh repo create <org>/loan-platform-backend --private --source=. --remote=origin
git push -u origin main
```

`.env`, `.venv/`, caches, and compiled lockfiles are already git-ignored — check
`git status` shows no secrets before the first push.

### Protect `main` (Settings → Branches → Add rule)

- ✅ **Require a pull request before merging** → require **1 approval**.
- ✅ **Require review from Code Owners** (uses [`.github/CODEOWNERS`](../.github/CODEOWNERS)).
- ✅ **Require status checks to pass** → select the **`ci`** check. ✅ **Require
  branches to be up to date**.
- ✅ **Require linear history** (we squash-merge).
- ✅ **Do not allow bypassing** the above.

CD also needs two **protected environments** (Settings → Environments):
`staging` and `production` (add required reviewers to `production`).

---

## 1. Daily workflow

### a. Start from fresh `main`

```bash
git switch main && git pull
git switch -c feat/rule-engine/RUL-12-add-dpd-column   # one service per branch
```

Branch names: `feat|fix|chore|docs|refactor|test/<service>/<ticket>-<slug>`.
Keep a branch scoped to **one** `src/app/services/<service>/` folder so two teams
never collide. (More in [`git_workflow.md`](git_workflow.md).)

### b. Run the gates locally **before** pushing

```powershell
.\dev.ps1 check        # ruff + black + mypy + pytest, in the dev container   (make check)
```
No local Python needed — this runs inside the **same image CI uses**, so green
locally ⇒ green in CI.

### c. Commit (Conventional Commits) and push

```bash
git commit -m "feat(rule-engine): add DPD input column"
git push -u origin HEAD
```

### d. Open the PR

```bash
gh pr create --fill            # or use the GitHub UI
```
The PR template + labeler run automatically. CODEOWNERS auto-requests the owning
team's review.

### e. CI runs → fix red → get review → merge

When all checks are green and a code owner approves:

```bash
gh pr merge --squash --delete-branch
git switch main && git pull
```

### Keeping up to date / conflicts

```bash
git fetch origin && git rebase origin/main
# resolve, then:
git rebase --continue
git push --force-with-lease
```
Rebase (don't merge `main` into your branch) so history stays linear.

---

## 2. What CI runs ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml))

Triggered on **every branch push** and on PRs into `main`. CI **builds the same
dev image you run locally** and executes the same commands inside it — so there's
no "works on my machine": identical Python and dependency versions everywhere.

One `ci` job, four steps:

| Step | Command (inside the container) | Fails when |
| ---- | ------------------------------ | ---------- |
| Build dev image | `docker compose … build api` | the image won't build |
| Lint + format + types | `ruff check . && black --check . && mypy src` | style / type errors |
| Tests | `pytest -q` | any test fails |
| Migrations | `migrate_sql.py` ×2 + `--status` against real Postgres | a migration fails or isn't idempotent |

### Reproduce any CI failure locally — one command

```powershell
.\dev.ps1 check          # lint + types + tests, the same image CI uses   (make check)
.\dev.ps1 migrate        # the migrations step                             (make migrate)
```

### Reading failures

```bash
gh pr checks                 # see if CI is red
gh run view --log-failed     # jump to the failing step's log
```
Common causes are catalogued in
[`docs/knowledge/Troubleshooting Log.md`](knowledge/Troubleshooting%20Log.md).

---

## 3. CD — build & deploy ([`.github/workflows/cd.yml`](../.github/workflows/cd.yml))

Runs on push to `main` and on `v*` tags.

```
push to main ─▶ build prod image ─▶ push to GHCR ─▶ deploy staging (auto)
tag v1.2.3   ─▶ ……………………………………………………………………… ─▶ deploy production (manual approval)
```

| Job | Trigger | Notes |
| --- | ------- | ----- |
| **build-and-push** | every `main` push / tag | builds `docker/api/Dockerfile` target `prod`, pushes `ghcr.io/<repo>/api:{latest,sha}` |
| **deploy-staging** | after build | protected `staging` environment |
| **deploy-production** | only on `v*` tag | protected `production` environment → **manual approval** |

> The deploy steps are `TODO(platform)` placeholders — wire them to your host
> (k8s/ECS/SSH) when infra is ready. The build/push half works as-is.

### Cut a release

```bash
git switch main && git pull
git tag v0.1.0 -m "release: v0.1.0"
git push origin v0.1.0      # triggers the production deploy (with approval)
```

---

## Quick reference

```bash
# start work
git switch main && git pull && git switch -c feat/<svc>/<ticket>-<slug>

# before pushing (the CI gates)
ruff check . && black . && mypy src && pytest -q

# ship
git commit -m "feat(<svc>): <subject>"
git push -u origin HEAD
gh pr create --fill
gh pr checks                       # watch CI
gh pr merge --squash --delete-branch

# release
git tag vX.Y.Z -m "release: vX.Y.Z" && git push origin vX.Y.Z
```

| Want to… | Go to |
| -------- | ----- |
| Branch / commit / merge rules | [`git_workflow.md`](git_workflow.md) |
| Onboard a new dev | [`../TEAM_ONBOARDING.md`](../TEAM_ONBOARDING.md) |
| Understand a CI error | [`knowledge/Troubleshooting Log.md`](knowledge/Troubleshooting%20Log.md) |
| Who owns which service | [`../.github/CODEOWNERS`](../.github/CODEOWNERS) |
