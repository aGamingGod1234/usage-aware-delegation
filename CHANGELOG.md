# Changelog

All notable changes to this skill are documented here.

## Unreleased

- Corrected Codex installation paths and made GitHub CLI agent and scope explicit.
- Parse skill and agent YAML during validation, reject duplicate keys and invalid
  field types, and check local file links throughout the package.
- Added regression tests for malformed packages and pinned validation-only
  YAML and Markdown parsers while preserving the existing policy-content checks.
- Updated CI actions and test Python 3.11 and 3.15 explicitly.

## 0.2.1 - 2026-09-09

- Rewrote the README around installation, task routing, usage, and
  verification.
- Removed redundant model-name explanations from the public documentation and
  skill references.

## 0.2.0 - 2026-09-09

- Added behavioral and harness fit alongside ambiguity, coupling, consequence,
  usage pressure, and coordination economics.
- Added a task-routing reference with frontend/UI, backend/API,
  research/planning, mechanical, debugging, review, and orchestration
  acceptance patterns.
- Added guarded fan-out conditions, completion-event guidance, and a fresh
  takeover path for stuck loops.
- Extended the contract test to cover the new reference and concepts.

## 0.1.0 - 2026-09-09

- Initial public release of the usage-aware-delegation Codex skill.
- Added capability-alias routing, effort selection, plan-pressure heuristics, delegation economics, child lifecycle rules, and evidence levels.
- Added model-routing and usage-and-agents references.
- Added GitHub installation documentation and a dependency-free repository contract test.
