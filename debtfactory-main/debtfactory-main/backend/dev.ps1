<#
.SYNOPSIS
  Docker-first task runner for Windows (the Makefile equivalent for PowerShell).
  No local Python needed — everything runs in the same dev image.

.EXAMPLE
  .\dev.ps1 up           # start the stack (api + db + redis + adminer)
  .\dev.ps1 test         # run the tests in a container
  .\dev.ps1 check        # lint + types + tests (what CI runs)
  .\dev.ps1 migrate      # apply SQL migrations
#>
param(
    [Parameter(Position = 0)] [string] $Command = "help",
    [Parameter(ValueFromRemainingArguments = $true)] $Rest
)

$DC = @("compose", "-f", "compose.yaml", "-f", "compose.dev.yaml")

switch ($Command) {
    "build"   { & docker @DC build api }
    "up"      { & docker @DC up --build db redis adminer api }
    "down"    { & docker @DC down }
    "clean"   { & docker @DC down -v }
    "logs"    { & docker @DC logs -f api }
    "shell"   { & docker @DC run --rm --no-deps api bash }
    "test"    { & docker @DC run --rm --no-deps api pytest -q @Rest }
    "lint"    { & docker @DC run --rm --no-deps api bash -lc "ruff check . && black --check . && mypy src" }
    "format"  { & docker @DC run --rm --no-deps api bash -lc "ruff check --fix . && black ." }
    "check"   { & docker @DC run --rm --no-deps api bash -lc "ruff check . && black --check . && mypy src && pytest -q" }
    "migrate" { & docker @DC run --rm api python scripts/migrate_sql.py @Rest }
    "jdm"     { & docker @DC run --rm --no-deps api python scripts/generate_jdm.py }
    default {
        Write-Host "Docker-first dev commands:" -ForegroundColor Cyan
        @(
            "  .\dev.ps1 build     Build the dev image",
            "  .\dev.ps1 up        Start the stack (api+db+redis+adminer, hot reload)",
            "  .\dev.ps1 down      Stop the stack",
            "  .\dev.ps1 clean     Stop + wipe the db volume",
            "  .\dev.ps1 logs      Tail API logs",
            "  .\dev.ps1 shell     Shell into the dev image",
            "  .\dev.ps1 test      Run tests in a container",
            "  .\dev.ps1 lint      ruff + black --check + mypy",
            "  .\dev.ps1 format    Auto-format (ruff --fix + black)",
            "  .\dev.ps1 check     lint + types + tests (what CI runs)",
            "  .\dev.ps1 migrate   Apply SQL migrations",
            "  .\dev.ps1 jdm       Regenerate the Rule Engine JDM"
        ) | ForEach-Object { Write-Host $_ }
    }
}
