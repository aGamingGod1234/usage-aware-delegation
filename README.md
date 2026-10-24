# Usage-aware delegation

[![Validate](https://github.com/SoulSniper-V2/usage-aware-delegation/actions/workflows/validate.yml/badge.svg)](https://github.com/SoulSniper-V2/usage-aware-delegation/actions/workflows/validate.yml)

A Codex skill for choosing between direct execution and bounded sub-agent work.
It routes by task shape, available runtime capabilities, usage pressure, and
the cost of verification.

## Install

### Codex

Use the built-in skill installer with:

    https://github.com/SoulSniper-V2/usage-aware-delegation/tree/main/skills/usage-aware-delegation

### GitHub CLI

    gh skill install SoulSniper-V2/usage-aware-delegation usage-aware-delegation --agent codex --scope user

Use a GitHub CLI version with `gh skill install` (currently a preview command).
For a single repository, run it there with `--scope project`. See the
[GitHub CLI install options](https://cli.github.com/manual/gh_skill_install).

### Skills CLI

    npx skills add SoulSniper-V2/usage-aware-delegation --skill usage-aware-delegation -a codex -g

Use project scope instead of -g when the skill should apply only to one
repository.

### Manual

    git clone https://github.com/SoulSniper-V2/usage-aware-delegation.git
    mkdir -p ~/.agents/skills
    cp -R usage-aware-delegation/skills/usage-aware-delegation ~/.agents/skills/usage-aware-delegation

For a repository-only manual install, use `.agents/skills` in that repository.
Copy into a new destination; check an existing installation before replacing it.
Codex detects skill changes automatically. Restart Codex if the skill does not
appear. See [Codex skill locations](https://learn.chatgpt.com/docs/build-skills#where-to-save-skills).

## Use it

Invoke it explicitly when you want the routing decision to be visible:

    Use $usage-aware-delegation. Inspect this repository, choose the smallest reliable route, and keep final integration and verification with me.

The skill can also be invoked implicitly when the current Codex runtime honors
the included agent metadata.

## How it works

The policy follows this order:

1. Honor the user's direct-work, model, effort, and delegation choices.
2. Preserve repository instructions, approvals, sandboxing, credentials, and
   external-action boundaries.
3. Inspect the runtime's available models, effort levels, sub-agent lifecycle,
   capacity, tools, and usage signals when the decision matters.
4. Classify the task and choose direct execution or bounded delegation.
5. Inspect the returned artifact and run the acceptance checks.

The default decision is direct execution. Delegate only when a child has a
self-contained objective, clear ownership, observable acceptance criteria, and
a model-fit or independent-overlap benefit that outweighs coordination cost.

## Direct or delegated?

| Prefer direct execution when | Consider a child when |
| --- | --- |
| The task is a question, tiny edit, exact probe, or tightly coupled sequence | The child has one independent, bounded objective |
| Work touches overlapping files or shared build/device state | The child is read-only or owns disjoint paths |
| The next step depends on the current result | Parallel work has a clear aggregation step |
| The action needs approval, credentials, deployment, or another external effect | A different capability or fresh review is likely to prevent expensive rework |
| Startup and context transfer cost more than the side work | Runtime capacity and child lifecycle are observable |

Direct tool or process concurrency comes before a second reasoning stream for
independent, safe commands. Keep dependent work, overlapping writes, builds,
approvals, and external actions serial.

## Task routing

Choose the route from the work, not from a fixed model recipe.

| Work | Starting point | Acceptance evidence |
| --- | --- | --- |
| Frontend, UI, design, 3D, or computer use | A model and harness with suitable visual or computer-use capability | Rendered browser/device inspection, interaction states, accessibility, and responsive behavior |
| Backend, API, integration, or data work | A balanced route; stronger review for auth, security, payments, or destructive changes | Tests, contracts, error paths, permissions, retries, and integration behavior |
| Research or planning | Direct or a bounded read-heavy sidecar | Dated sources, contradictions, assumptions, and explicit plan acceptance |
| Mechanical or repeatable work | Direct or a bounded low-cost route | Exact diff, focused test, formatter, or inventory result |
| Unknown cross-system debugging | A bounded investigation with enough reasoning depth for the coupling | Reproduction, root-cause evidence, and a regression check where possible |
| Independent review | Fresh, read-only context when risk justifies it | Findings tied to behavior or paths, severity, and supporting evidence |
| Orchestration | A runtime with observable child lifecycle and a coordinator that owns integration | Child contracts, ownership, terminal state, aggregation, and final verification |

See [task-routing.md](skills/usage-aware-delegation/references/task-routing.md)
for the full matrix and workflow patterns.

## Usage and effort

Usage pressure changes optional work before it changes safety requirements:

- ample capacity: use the normal benefit gate and a small amount of fan-out;
- watch: prefer direct work, use at most one child for a clear benefit, and
  skip optional review;
- conserve: stay direct unless delegation avoids likely expensive failure;
- exhausted: continue locally if possible and stop optional work;
- unknown: assume conservative capacity and avoid quota claims.

Use the lowest effort that is sufficient for the task. Medium is the normal
starting point; higher effort is for difficult, coupled, consequential, or
verification-heavy work. Native Ultra is never selected automatically.

The skill does not predict turns from token counts. It records usage only when
the runtime exposes a current read-only signal.

## Operating rules

- The coordinator owns intent, architecture, approvals, conflicts, integration,
  and final verification.
- Every child gets a bounded contract, exact scope, ownership, acceptance
  checks, a validation budget, and a stop condition.
- Children do not delegate recursively or write to overlapping paths.
- A child report is not proof that its artifact or tests passed.
- A missing dependency, permission, credential, or external service is not
  evidence that a stronger model is needed.
- A stuck loop gets a fresh, bounded takeover with the current state preserved.
- A recommendation is reported separately from a dispatch that the runtime
  actually accepted and observed.

The runtime still controls model availability, effort support, child lifecycle,
and external permissions. When it cannot provide evidence, the skill says so.

## Package layout

    .
    ├── skills/usage-aware-delegation/
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   └── references/
    │       ├── model-routing.md
    │       ├── task-routing.md
    │       └── usage-and-agents.md
    ├── tests/
    │   ├── test_skill_contract.py
    │   └── test_validator.py
    ├── requirements-dev.txt
    ├── .github/workflows/validate.yml
    ├── CHANGELOG.md
    ├── CONTRIBUTING.md
    └── LICENSE

The canonical skill lives under skills/usage-aware-delegation. The root README
is for people; it is not duplicated inside the skill directory.

## Validate

The installed skill has no runtime dependencies. Repository validation needs
Python 3.11 or newer and the pinned development dependencies:

    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements-dev.txt
    .venv/bin/python tests/test_skill_contract.py
    .venv/bin/python -m unittest discover -s tests -v

On Windows, use `.venv\Scripts\python.exe` in place of `.venv/bin/python`.
The checks parse YAML metadata, validate the invocation policy and local
Markdown file links, and exercise malformed-package regressions. They do not
measure an agent's routing decisions or validate remote links.

If the Codex skill creator is installed:

    .venv/bin/python /path/to/codex/skills/.system/skill-creator/scripts/quick_validate.py skills/usage-aware-delegation

Also check the patch:

    git diff --check

## References

- [Sub-agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Plan usage](https://learn.chatgpt.com/docs/pricing)
- [Reasoning effort](https://developers.openai.com/api/docs/guides/reasoning)
- [Task routing reference](skills/usage-aware-delegation/references/task-routing.md)
- [Model routing reference](skills/usage-aware-delegation/references/model-routing.md)
- [Usage and lifecycle reference](skills/usage-aware-delegation/references/usage-and-agents.md)

Model availability, plan behavior, and runtime schemas change. Re-check the
current documentation before relying on a dated model or usage assumption.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before changing the routing contract.
Keep changes focused, explain the evidence behind new rules, and preserve the
distinction between recommendations, observed execution, and verified results.

## License

MIT. See [LICENSE](LICENSE).
