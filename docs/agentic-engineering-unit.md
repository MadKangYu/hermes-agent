# Agentic Engineering Unit Protocol

Hermes Agent work should be dispatchable, resumable, auditable, and safe to
retry. Treat every non-trivial Hermes task as one unit with a stated goal,
state, authority boundary, verification gate, log location, and completion
condition.

## Unit Template

```text
unit_id:
surface:
goal:
current_state:
authority_boundary:
verification_criteria:
log_location:
completion_condition:
contract_category:
status:
```

Use stable ASCII for `unit_id` and `surface` so the same handle can appear in
terminal logs, kanban tasks, commits, Obsidian notes, and future dispatches.
The validator accepts lowercase ASCII `unit_id` values made from letters,
digits, and hyphens.

## Surface Map

| Surface | Primary state | Typical verification |
| --- | --- | --- |
| `core` | `run_agent.py`, `model_tools.py`, `agent/` | `scripts/run_tests.sh <target>`, cache/loop invariant test |
| `cli` | `cli.py`, `hermes_cli/` | `scripts/run_tests.sh <target>`, `--help`/dry-run output, path check |
| `gateway` | `gateway/run.py`, `gateway/session.py` | `scripts/run_tests.sh tests/gateway/`, queue/control-command evidence |
| `platform` | `gateway/platforms/<name>.py` | adapter test via `scripts/run_tests.sh`, token-lock proof, dry-run/live split |
| `plugin` | `plugins/<name>/` | plugin tests via `scripts/run_tests.sh`, config/template verification |
| `skill` | `skills/`, `optional-skills/` | loader test via `scripts/run_tests.sh`, frontmatter validation, scoped smoke check |
| `profile` | `get_hermes_home()` target | profile path proof, profile log/session evidence |
| `cron` | `cron/`, `~/.hermes/cron/` | job store/scheduler test, no runaway-session risk |
| `kanban` | board database and task history | task state transition proof, blocker/result record |
| `website` | `website/` | build or route check, browser-visible body marker |
| `docs` | `docs/`, `AGENTS.md` | `git diff --check`, path/link/secret scan |

## Authority Boundaries

Local repo source, tests, docs, fixtures, and non-secret templates are normally
inside scope. The following are outside scope unless the active unit explicitly
grants authority:

- `.env`, `auth/`, token stores, OAuth credentials, API keys.
- Slack live app scopes, admin approvals, service tokens, or external sends.
- Production gateway deployments or long-running daemons.
- Browser profiles containing live user data.
- Deletes, resets, force pushes, or irreversible data migrations.

When the work touches Slack, keep each gate separate: manifest valid, app
installed, config token present, runtime token authenticated, required scopes
granted, admin approval complete, dry-run passed, live write approved.

## Verification Categories

- `api-contract`: public function, CLI, gateway, platform, plugin, or tool schema
  behavior that callers depend on.
- `state-contract`: session DB, profile path, cache, memory, kanban, cron, or
  lock behavior.
- `auth-contract`: credentials, token lock, scopes, approvals, or permission
  boundaries.
- `runtime-contract`: process lifecycle, background notification, interrupt,
  timeout, or scheduler behavior.
- `ui-contract`: TUI, ACP, website, dashboard, or browser-visible behavior.
- `data-contract`: schema, fixture, migration, serialization, import/export.
- `integration-contract`: Slack, Telegram, browser/CDP, Obsidian, OMX, Codex, or
  other external system boundary.

## Failure Learning Loop

Failed verification is not noise. Record it in the unit ledger with the failed
gate, root cause if known, fallback used, and the next check that would prevent
the same failure from recurring.

Use this shape:

```text
failure:
  failed_gate:
  observed_error:
  likely_contract_gap:
  fix_or_fallback:
  next_regression_check:
```

Regression checks should be invariant/contract tests. Do not add tests that
only snapshot routine catalog growth, config version numbers, model names, or
other expected churn.

## Example Units

```text
unit_id: slack-canvas-token-gate-2026-05-13
surface: platform
goal: Separate Slack manifest success from runtime Canvas write readiness.
current_state: Manifest validation passes, but live Canvas write requires token/scope/admin evidence.
authority_boundary: Edit adapter tests/docs only; do not request scopes or send Slack messages.
verification_criteria: Targeted Slack adapter checks pass via `scripts/run_tests.sh` and docs name every readiness gate.
log_location: docs/plans/slack-canvas-token-gate-2026-05-13.md
completion_condition: Tests pass, gates documented, no live Slack mutation performed.
contract_category: auth-contract
status: planned
```

```text
unit_id: madstamp-profile-memory-sync-2026-05-13
surface: profile
goal: Record reusable Madstamp operating state without contaminating default Hermes state.
current_state: Active profile path must be proven before writing memory.
authority_boundary: Write profile memory and Obsidian note only; do not edit tokens or gateway config.
verification_criteria: `get_hermes_home()` target is shown and the new memory file exists under that profile.
log_location: ~/.hermes/profiles/madstamp/memories/
completion_condition: Profile-local file exists and Obsidian note links the evidence.
contract_category: state-contract
status: planned
```

## Closeout Checklist

Before closing a unit:

- The completion condition is met with fresh evidence.
- `.venv/bin/python scripts/check_agentic_unit.py <unit-ledger.md>` passes for
  markdown unit ledgers, including required fields, valid `surface`, valid
  `contract_category`, valid `status`, and lowercase ASCII `unit_id`.
- CI validates discovered unit ledgers in `docs/plans/` through
  `.github/workflows/agentic-unit-check.yml`.
- Failed attempts, fallbacks, and rejected paths are captured.
- The log location exists and can be inspected later.
- Tests or smoke checks were run, or the reason they could not run is explicit.
- No secret, token, or profile-user-data mutation happened outside authority.
