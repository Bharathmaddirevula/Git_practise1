# Loan Platform Backend — Docker-first task runner.
# No local Python needed: every command runs inside the same dev image, so the
# whole team (and CI) runs the exact same versions.
.DEFAULT_GOAL := help
DC := docker compose -f compose.yaml -f compose.dev.yaml
DC_PROD := docker compose -f compose.yaml -f compose.prod.yaml

.PHONY: help
help: ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: ## Build the dev image.
	$(DC) build api

.PHONY: up
up: ## Start the dev stack (api + db + redis + adminer) with hot reload.
	$(DC) up --build db redis adminer api

.PHONY: down
down: ## Stop the stack.
	$(DC) down

.PHONY: clean
clean: ## Stop the stack and wipe the database volume.
	$(DC) down -v

.PHONY: logs
logs: ## Tail the API logs.
	$(DC) logs -f api

.PHONY: shell
shell: ## Open a shell in the dev image.
	$(DC) run --rm --no-deps api bash

.PHONY: test
test: ## Run the test suite in a container.
	$(DC) run --rm --no-deps api pytest -q

.PHONY: lint
lint: ## ruff + black --check + mypy in a container.
	$(DC) run --rm --no-deps api bash -lc "ruff check . && black --check . && mypy src"

.PHONY: format
format: ## Auto-format (ruff --fix + black) in a container.
	$(DC) run --rm --no-deps api bash -lc "ruff check --fix . && black ."

.PHONY: check
check: ## Everything CI runs: lint + types + tests.
	$(DC) run --rm --no-deps api bash -lc "ruff check . && black --check . && mypy src && pytest -q"

.PHONY: migrate
migrate: ## Apply SQL migrations against the running db.
	$(DC) run --rm api python scripts/migrate_sql.py

.PHONY: migrate-status
migrate-status: ## Show applied vs pending migrations.
	$(DC) run --rm api python scripts/migrate_sql.py --status

.PHONY: jdm
jdm: ## Regenerate the Rule Engine JDM artifact from the matrix.
	$(DC) run --rm --no-deps api python scripts/generate_jdm.py

.PHONY: prod-config
prod-config: ## Validate the prod compose configuration.
	$(DC_PROD) config
