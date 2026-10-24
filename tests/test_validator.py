"""Exercise the actual validator command against valid and broken packages."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_skill_contract import REQUIRED, ROOT, SKILL_PATH


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in (*REQUIRED, 'tests/test_skill_contract.py'):
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)

    def replace(self, name, old, new):
        path = self.root / name
        text = path.read_text(encoding='utf-8')
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding='utf-8')

    def run_validator(self, expected=0, error=''):
        result = subprocess.run(
            [sys.executable, str(self.root / 'tests/test_skill_contract.py')],
            cwd=self.root, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        self.assertIn(error, result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def frontmatter(self, value):
        path = self.root / SKILL_PATH / 'SKILL.md'
        _, _, body = path.read_text(encoding='utf-8').split('---', 2)
        path.write_text(f'---\n{value}\n---{body}', encoding='utf-8')

    def test_published_package(self):
        self.run_validator()

    def test_yaml_block_description(self):
        self.frontmatter('name: usage-aware-delegation\ndescription: >-\n  Route bounded work\n  with runtime evidence.')
        self.run_validator()

    def test_invalid_frontmatter_yaml(self):
        self.frontmatter('name: usage-aware-delegation\ndescription: [unfinished')
        self.run_validator(1, 'invalid YAML')

    def test_non_mapping_frontmatter(self):
        self.frontmatter('- name: usage-aware-delegation\n- description: Routing')
        self.run_validator(1, 'must be a YAML mapping')

    def test_invalid_descriptions(self):
        for value in ('false', '[]', '"  "', '|\n  ' + 'x' * 1025):
            with self.subTest(value=value[:30]):
                self.frontmatter(f'name: usage-aware-delegation\ndescription: {value}')
                self.run_validator(1, 'description must be a non-empty string')

    def test_duplicate_keys(self):
        self.frontmatter('name: other\nname: usage-aware-delegation\ndescription: Routing')
        self.run_validator(1, 'duplicate YAML mapping key')

    def test_incomplete_delimiter(self):
        self.replace(SKILL_PATH / 'SKILL.md', '\n---\n', '\n---oops\n')
        self.run_validator(1, 'complete YAML frontmatter delimiters')

    def test_invalid_agent_yaml(self):
        self.replace(SKILL_PATH / 'agents/openai.yaml', 'interface:', 'interface: [')
        self.run_validator(1, 'invalid YAML')

    def test_commented_policy_is_not_enabled(self):
        self.replace(SKILL_PATH / 'agents/openai.yaml', '  allow_implicit_invocation:', '  # allow_implicit_invocation:')
        self.run_validator(1, 'policy.allow_implicit_invocation')

    def test_string_true_is_not_a_boolean(self):
        self.replace(SKILL_PATH / 'agents/openai.yaml', 'allow_implicit_invocation: true', 'allow_implicit_invocation: "true"')
        self.run_validator(1, 'policy.allow_implicit_invocation')

    def test_invalid_brand_colors(self):
        path = self.root / SKILL_PATH / 'agents/openai.yaml'
        original = path.read_text(encoding='utf-8')
        for value in ('[]', '"not-a-color"', '"#123"'):
            with self.subTest(value=value):
                path.write_text(original.replace('"#6D5EF8"', value), encoding='utf-8')
                self.run_validator(1, 'brand_color must be a six-digit hex color')

    def test_brand_color_is_optional(self):
        self.replace(SKILL_PATH / 'agents/openai.yaml', '  brand_color: "#6D5EF8"\n', '')
        self.run_validator()

    def test_missing_required_file(self):
        (self.root / SKILL_PATH / 'references/model-routing.md').unlink()
        self.run_validator(1, 'missing required file')

    def test_broken_reference_link(self):
        with (self.root / SKILL_PATH / 'references/task-routing.md').open('a') as stream:
            stream.write('\n[missing](missing.md)\n')
        self.run_validator(1, 'broken or out-of-package link')

    def test_reference_link_cannot_escape_installed_skill(self):
        with (self.root / SKILL_PATH / 'SKILL.md').open('a') as stream:
            stream.write('\n[root README](../../README.md)\n')
        self.run_validator(1, 'out-of-package link')

    def test_broken_links_with_titles(self):
        path = self.root / SKILL_PATH / 'references/task-routing.md'
        original = path.read_text(encoding='utf-8')
        for title in ('"a title"', "'a title'", '(a title)'):
            with self.subTest(title=title):
                path.write_text(original + f'\n[missing](missing.md {title})\n', encoding='utf-8')
                self.run_validator(1, 'broken or out-of-package link')

    def test_titled_link_cannot_escape_installed_skill(self):
        with (self.root / SKILL_PATH / 'SKILL.md').open('a') as stream:
            stream.write('\n[root README](../../README.md "outside skill")\n')
        self.run_validator(1, 'out-of-package link')

    def test_valid_link_with_title_and_angle_destination(self):
        with (self.root / SKILL_PATH / 'SKILL.md').open('a') as stream:
            stream.write('\n[routing](<references/task-routing.md> "routing guide")\n')
        self.run_validator()

    def test_missing_and_escaping_parenthesized_links(self):
        path = self.root / SKILL_PATH / 'SKILL.md'
        original = path.read_text(encoding='utf-8')
        for target in ('references/missing(v2).md', '../../outside(v2).md', r'references/missing\(v2\).md'):
            with self.subTest(target=target):
                path.write_text(original + f'\n[guide]({target})\n', encoding='utf-8')
                self.run_validator(1, 'broken or out-of-package link')

    def test_existing_parenthesized_link(self):
        (self.root / SKILL_PATH / 'references/guide(v2).md').write_text('Guide', encoding='utf-8')
        with (self.root / SKILL_PATH / 'SKILL.md').open('a') as stream:
            stream.write('\n[guide](references/guide(v2).md)\n')
        self.run_validator()

    def test_empty_skill_body_cannot_pass(self):
        path = self.root / SKILL_PATH / 'SKILL.md'
        frontmatter = path.read_text(encoding='utf-8').split('---', 2)[1]
        path.write_text(f'---{frontmatter}---\n# Usage-aware delegation\n', encoding='utf-8')
        (self.root / SKILL_PATH / 'references/task-routing.md').write_text('', encoding='utf-8')
        self.run_validator(1, 'credential boundary')

    def test_machine_specific_user_path(self):
        with (self.root / SKILL_PATH / 'SKILL.md').open('a') as stream:
            stream.write('\n/Users/example/private\n')
        self.run_validator(1, 'machine-specific')

    def test_file_link_with_fragment(self):
        with (self.root / SKILL_PATH / 'SKILL.md').open('a') as stream:
            stream.write('\n[routing](references/task-routing.md#task-shape-matrix)\n')
        self.run_validator()


if __name__ == '__main__':
    unittest.main()
