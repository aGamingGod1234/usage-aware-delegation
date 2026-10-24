#!/usr/bin/env python3
"""Validate the published package's YAML metadata and local file links."""

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

import yaml
from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = Path('skills/usage-aware-delegation')
REQUIRED = (
    'README.md', 'LICENSE', 'CONTRIBUTING.md', 'CHANGELOG.md', '.gitignore',
    'requirements-dev.txt', '.github/workflows/validate.yml',
    str(SKILL_PATH / 'SKILL.md'), str(SKILL_PATH / 'agents/openai.yaml'),
    str(SKILL_PATH / 'references/model-routing.md'),
    str(SKILL_PATH / 'references/task-routing.md'),
    str(SKILL_PATH / 'references/usage-and-agents.md'),
)


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate keys instead of silently replacing a policy value."""

    def construct_mapping(self, node, deep=False):
        mapping = super().construct_mapping(node, deep=deep)
        keys = [self.construct_object(key, deep=deep) for key, _ in node.value]
        if len(keys) != len(set(keys)):
            raise yaml.constructor.ConstructorError(
                None, None, 'duplicate YAML mapping key', node.start_mark
            )
        return mapping


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def load_mapping(text: str, label: str, failures: list[str]) -> dict:
    try:
        value = yaml.load(text, Loader=UniqueKeyLoader)
    except yaml.YAMLError as exc:
        failures.append(f'{label}: invalid YAML: {exc}')
        return {}
    if not isinstance(value, dict):
        failures.append(f'{label}: must be a YAML mapping')
        return {}
    return value


def nonempty_string(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for name in REQUIRED:
        check((root / name).is_file(), f'missing required file: {name}', failures)
    if failures:
        return failures

    skill = root / SKILL_PATH
    skill_text = (skill / 'SKILL.md').read_text(encoding='utf-8')
    match = re.match(r'\A---\n(.*?)\n---(?:\n|\Z)', skill_text, re.DOTALL)
    check(match is not None, 'SKILL.md needs complete YAML frontmatter delimiters', failures)
    frontmatter = load_mapping(match[1], 'SKILL.md frontmatter', failures) if match else {}
    check(frontmatter.get('name') == skill.name, 'frontmatter name must match skill directory', failures)
    description = frontmatter.get('description')
    check(
        nonempty_string(description) and len(description) <= 1024,
        'frontmatter description must be a non-empty string of at most 1024 characters',
        failures,
    )
    if 'metadata' in frontmatter:
        metadata = frontmatter['metadata']
        check(
            isinstance(metadata, dict)
            and all(isinstance(k, str) and isinstance(v, str) for k, v in metadata.items()),
            'frontmatter metadata must map strings to strings', failures,
        )

    agent = load_mapping(
        (skill / 'agents/openai.yaml').read_text(encoding='utf-8'),
        'agents/openai.yaml', failures,
    )
    interface = agent.get('interface')
    if not isinstance(interface, dict):
        failures.append('agents/openai.yaml needs an interface mapping')
    else:
        for key in ('display_name', 'short_description', 'default_prompt'):
            check(nonempty_string(interface.get(key)), f'interface.{key} must be a non-empty string', failures)
        check(
            '$usage-aware-delegation' in str(interface.get('default_prompt', '')),
            'interface.default_prompt must invoke $usage-aware-delegation', failures,
        )
        if 'brand_color' in interface:
            color = interface['brand_color']
            check(
                isinstance(color, str) and re.fullmatch(r'#[0-9A-Fa-f]{6}', color) is not None,
                'interface.brand_color must be a six-digit hex color', failures,
            )
    policy = agent.get('policy')
    check(
        isinstance(policy, dict) and policy.get('allow_implicit_invocation') is True,
        'policy.allow_implicit_invocation must be the boolean true', failures,
    )

    # Skill links must survive installation without the surrounding repository.
    parser = MarkdownIt('commonmark')
    documents = [*root.glob('*.md'), *skill.rglob('*.md')]
    for path in documents:
        boundary = skill.resolve() if path.is_relative_to(skill) else root.resolve()
        for block in parser.parse(path.read_text(encoding='utf-8')):
            for token in block.children or ():
                target = token.attrGet('href') if token.type == 'link_open' else token.attrGet('src')
                if target is None:
                    continue
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path:
                    continue
                resolved = (path.parent / unquote(url.path)).resolve()
                check(
                    resolved.is_relative_to(boundary) and resolved.is_file(),
                    f'{path.relative_to(root)}: broken or out-of-package link: {target}',
                    failures,
                )

    check("/Users/" not in skill_text, "SKILL.md must not contain a machine-specific /Users path", failures)
    check("credential" in skill_text.lower(), "skill should state its credential boundary", failures)
    check("external actions" in skill_text.lower(), "skill should state its external-action boundary", failures)
    check("Behavioral and harness fit" in skill_text, "skill should cover behavioral and harness fit", failures)
    check("task-routing.md" in skill_text, "skill should link task-routing.md", failures)
    task_text = (skill / "references" / "task-routing.md").read_text(encoding="utf-8") if (skill / "references" / "task-routing.md").is_file() else ""
    for phrase in (
        "Model versus harness",
        "Task-shape matrix",
        "Stuck-loop fresh takeover",
        "completion events",
    ):
        check(phrase.lower() in task_text.lower(), f"task-routing.md missing required concept: {phrase}", failures)

    return failures


def main() -> int:
    failures = validate(ROOT)
    if failures:
        for failure in failures:
            print(f'FAIL: {failure}', file=sys.stderr)
        return 1
    print('usage-aware-delegation contract: PASS')
    print(f'checked {len(REQUIRED)} required files, YAML metadata, and local Markdown file links')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
