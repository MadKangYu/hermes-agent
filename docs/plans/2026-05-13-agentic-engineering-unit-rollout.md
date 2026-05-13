# Hermes Agentic Engineering Unit Rollout

unit_id: hermes-agentic-engineering-unit-rollout-2026-05-13
surface: docs
goal: Make Hermes Agent work dispatchable, resumable, auditable, and verifiable as agentic engineering units.
current_state: The user-level `/Users/yu/AGENTS.md` already defines the cross-surface unit protocol; Hermes Agent repo needed a Hermes-specific contract for profiles, gateway/platform work, Slack gates, browser/CDP evidence, logs, and closeout.
authority_boundary: Edit Hermes Agent repo docs and agent instructions only. Do not mutate secrets, auth state, live Slack app scopes, gateway runtime, browser user profiles, or production deployment state.
verification_criteria: `git diff --check` passes for changed docs, required unit fields are present in `AGENTS.md` and `docs/agentic-engineering-unit.md`, and this rollout plan records the close gate.
log_location: `docs/plans/2026-05-13-agentic-engineering-unit-rollout.md`
completion_condition: Hermes-specific contract exists in `AGENTS.md`, reusable protocol doc exists under `docs/`, this rollout ledger exists under `docs/plans/`, and verification commands pass.
contract_category: runtime-contract
status: verified

## Changes

- Added `Agentic Engineering Unit Contract` to the repo-level `AGENTS.md`.
- Added reusable protocol/template documentation at `docs/agentic-engineering-unit.md`.
- Added this rollout ledger so the protocol application is itself auditable.
- Added a separate Hermes runtime memory note at
  `/Users/yu/.hermes/memories/agentic-engineering-unit-protocol-2026-05-13.md`
  without editing the existing `MEMORY.md`/`USER.md` files.
- Added `scripts/check_agentic_unit.py` plus focused tests so unit ledgers can
  be mechanically checked for required fields, valid status, valid surface,
  valid contract category, and lowercase ASCII unit id.
- Connected the validator to CI with `.github/workflows/agentic-unit-check.yml`
  so `docs/plans/` unit ledgers are checked even when the main test workflow
  ignores docs-only changes.
- Deepened the contract after review to align with Hermes' existing test wrapper
  rule: use `scripts/run_tests.sh`, not direct `pytest`, and prefer invariant
  regression tests over change-detector tests.

## Verification Log

- PASS: `git diff --check -- AGENTS.md docs/agentic-engineering-unit.md docs/plans/2026-05-13-agentic-engineering-unit-rollout.md`
- PASS: `rg -n "unit_id:|surface:|goal:|current_state:|authority_boundary:|verification_criteria:|log_location:|completion_condition:|contract_category:|status:" AGENTS.md docs/agentic-engineering-unit.md docs/plans/2026-05-13-agentic-engineering-unit-rollout.md`
- PASS: `rg -n "\\.env|auth/|Slack|Browser/CDP|HERMES_HOME|get_hermes_home\\(\\)|git diff --check" AGENTS.md docs/agentic-engineering-unit.md docs/plans/2026-05-13-agentic-engineering-unit-rollout.md`
- PASS: review found and corrected a conflict with the existing Testing section
  that forbids direct `pytest` as the normal path.
- PASS: corrected shell quoting after a verification command accidentally let
  backticks execute under zsh.
- PASS: trailing whitespace check on all changed files.
- PASS_WITH_CONTEXT: secret-pattern scan only matched an existing documented
  query parameter example in `AGENTS.md`; no new secret or token literal was
  introduced by this unit.
- PASS: runtime memory note exists as a separate file and does not alter existing
  Hermes `MEMORY.md` or `USER.md`.
- PASS: `scripts/run_tests.sh tests/scripts/test_check_agentic_unit.py` (`10 passed`)
- PASS: `.venv/bin/python scripts/check_agentic_unit.py docs/plans/2026-05-13-agentic-engineering-unit-rollout.md /Users/yu/.hermes/memories/agentic-engineering-unit-protocol-2026-05-13.md`
- PASS: validator deepening caught the earlier loose spots: invalid `surface`,
  invalid `contract_category`, and non-ASCII `unit_id` now fail tests.
- PASS: `.venv/bin/python scripts/check_agentic_unit.py --discover docs/plans`
- PASS: `.github/workflows/agentic-unit-check.yml` parses as YAML
- PASS: `.venv/bin/python scripts/check_agentic_unit.py --discover /tmp/definitely-missing-agentic-unit-dir` fails with `path does not exist`

failure:
  failed_gate: validator test after CI discovery wiring
  observed_error: discovery test assumed `rglob` result ordering returned top-level files before nested files
  likely_contract_gap: discovery behavior requires membership correctness, not path-order stability
  fix_or_fallback: changed the assertion to compare sets of discovered paths
  next_regression_check: avoid order-sensitive assertions unless ordering is the contract being tested

failure:
  failed_gate: validator discover missing-path behavior
  observed_error: `--discover` returned PASS when the supplied root path did not exist
  likely_contract_gap: empty discovery and invalid input were collapsed into the same success case
  fix_or_fallback: missing paths now fail before discovery starts
  next_regression_check: keep a regression test for missing discovery roots

failure:
  failed_gate: concrete unit discovery
  observed_error: regex used `\s*`, so an empty `unit_id:` could consume the newline and treat the next field as the unit id value
  likely_contract_gap: Python `\s` includes newline; discovery needed horizontal whitespace only
  fix_or_fallback: changed discovery regex to `[ \t]*\S+`
  next_regression_check: empty `unit_id:` templates must not be discovered as concrete unit ledgers

## Failure Learning

failure:
  failed_gate: verification command hygiene
  observed_error: zsh attempted to execute backticked `pytest` while running an `rg` command
  likely_contract_gap: verification commands that search for markdown backticks must be single-quoted or escaped
  fix_or_fallback: reran the search with single quotes and recorded this failure
  next_regression_check: prefer single-quoted `rg` patterns when matching markdown inline code

failure:
  failed_gate: standalone validator invocation
  observed_error: local shell returned `zsh:1: command not found: python`
  likely_contract_gap: Hermes instructions assume an active venv for bare `python`, but Codex shell commands may not have one activated
  fix_or_fallback: reran the validator with `.venv/bin/python`
  next_regression_check: document validator examples with `.venv/bin/python` or active-venv wording

## Closeout

The unit is verified for docs plus validator scope. The targeted validator test
suite passed. Broader Hermes tests were not run because no agent loop, gateway,
profile, provider, database, or runtime production path changed.
