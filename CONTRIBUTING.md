# Contributing

Thanks for helping improve usage-aware delegation.

## Before you change a policy

Read the canonical skill in skills/usage-aware-delegation/SKILL.md and the relevant reference file. Keep the policy model-agnostic where possible. Current model names, plan limits, runtime schemas, and native lifecycle behavior can change, so verify fast-moving claims against current first-party documentation.

Every routing rule should answer:

- What observable task evidence triggers it?
- Why does the route repay coordination cost?
- What is the fallback when the preferred model or tool is unavailable?
- How is actual execution distinguished from a recommendation?
- What is the safety boundary for credentials, approvals, writes, and external actions?
- Which check proves the rule worked?

## Change scope

- Keep the canonical skill under skills/usage-aware-delegation/.
- Put human-facing package documentation at the repository root.
- Keep workers bounded, non-recursive, and explicit about ownership.
- Do not add secrets, cookies, private prompts, account identifiers, or raw session logs.
- Do not hard-code a model as available solely because a benchmark, Reddit comment, or social post mentions it.
- Preserve unrelated user changes when working from a local checkout.

## Validation

Use Python 3.11 or newer. Run these commands from the repository root:

    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements-dev.txt
    .venv/bin/python tests/test_skill_contract.py
    .venv/bin/python -m unittest discover -s tests -v
    git diff --check

On Windows, use `.venv\Scripts\python.exe` for the virtual environment.
CI exercises Python 3.11 and 3.15. The installed skill remains dependency-free;
PyYAML and markdown-it-py are only used to validate repository metadata and links. Regression tests run the
actual checker against temporary copies, including invalid YAML and missing
references. Policy quality still requires review or a bounded routing exercise.

If you have a Codex installation, run the skill creator validator too:

    .venv/bin/python /path/to/codex/skills/.system/skill-creator/scripts/quick_validate.py skills/usage-aware-delegation

For changes to references or routing behavior, include a short note in the pull request describing the evidence and the expected behavior change.

## Pull requests

Use a focused title and explain:

1. the problem;
2. the policy or documentation change;
3. the evidence and source date;
4. the validation commands and results;
5. any remaining uncertainty or runtime-specific limitation.

Do not describe a recommendation as a measured speedup, quota saving, model switch, or quality improvement without direct evidence.
