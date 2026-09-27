"""Regression checks for the public modules reference renderer."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('render_modules', Path(__file__).with_name('render_modules.py'))
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class ModuleRenderingTests(unittest.TestCase):
    def test_requirements_preserve_statement_level_and_verification(self):
        result = renderer.render([{'id': 'req-001', 'level': 'L2',
                                   'statement': 'Every agent MUST present evidence.',
                                   'verification': 'Conformance test TEST-01'}])
        for expected in ['req-001', 'L2', 'Every agent MUST present evidence.',
                         'Conformance test TEST-01']:
            self.assertIn(expected, result)

    def test_unknown_nested_fields_and_falsy_values_are_retained(self):
        result = renderer.render({'future_field': {'enabled': False, 'count': 0,
                                                  'nullable': None, 'options': []}})
        for expected in ['Future field', 'enabled', 'false', 'count', '>0<', 'null', '[]']:
            self.assertIn(expected, result)

    def test_source_html_is_escaped(self):
        result = renderer.render({'description': '<script>alert("x")</script>'})
        self.assertNotIn('<script>', result)
        self.assertIn('&lt;script&gt;', result)

    def test_malformed_or_empty_yaml_fails_without_publishing(self):
        for raw in ['module: [', '', '[]']:
            with self.subTest(raw=raw), tempfile.TemporaryDirectory() as directory:
                repo = Path(directory)
                module = repo / 'spec/part-03-information-model/model.yaml'
                module.parent.mkdir(parents=True)
                module.write_text(raw)
                output = repo / '_site'
                output.mkdir()
                template = repo / 'template.html'
                template.write_text('<head></head><h1>{{TITLE}}</h1>{{CONTENT}}')
                with self.assertRaises(ValueError):
                    renderer.build(repo, output, template)
                self.assertFalse((output / 'modules.html').exists())

    def test_complete_source_download_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            module = repo / 'spec/part-03-information-model/model.yaml'
            module.parent.mkdir(parents=True)
            original = b'# Original source comment\nmodule: example\nfields:\n  unit:\n    type: string\n'
            module.write_bytes(original)
            output = repo / '_site'
            output.mkdir()
            template = repo / 'template.html'
            template.write_text('<head></head><h1>{{TITLE}}</h1>{{CONTENT}}')
            renderer.build(repo, output, template)
            downloaded = output / 'module-sources/part-03-information-model/model.yaml'
            self.assertEqual(original, downloaded.read_bytes())
            html = (output / 'modules.html').read_text()
            self.assertEqual(html.count('<h1>'), 1)
            self.assertIn('module-part-03-information-model-model', html)


if __name__ == '__main__':
    unittest.main()
