#!/usr/bin/env python3
"""Render the YAML modules as structured reference documentation.

Every parsed field is retained; source YAML is copied without modification.
Invalid or empty module files fail the site build rather than publishing blanks.
"""
from html import escape
from pathlib import Path
import re
import shutil
import sys

import yaml


MODULES = {
    'INFORMATION-MODEL': ('Information model', 'Agents, capabilities, tasks, resources and evidence records.'),
    'availability_provider_contract': ('Availability provider contract', 'Interfaces for workforce availability and allocation.'),
    'task_source_contract': ('Task source contract', 'Interfaces for submitting and updating operational tasks.'),
    'capability-registry': ('Capability registry', 'Capability identifiers, parameters and conformance references.'),
    'identity-trust': ('Identity and trust', 'Machine identity, transport security and verification requirements.'),
    'data_governance_module': ('Data governance', 'Data classes, permitted flows and governance requirements.'),
}

STYLE = '''
.docheader, .content.modules-content { max-width: 1100px; }
.modules-intro { max-width: 680px; }
.module-section { scroll-margin-top: 75px; margin-top: 2.5rem; }
.module-section h2 { font-size: 1.3rem; }
.module-section h3 { font-size: 1rem; }
.module-meta { color: #4a5568; font-size: .8rem; }
.module-table-scroll { max-width: 100%; overflow-x: auto; margin: .75rem 0 1rem; }
.module-table-scroll:focus-visible, .module-details summary:focus-visible {
  outline: 2px solid #0a2c77; outline-offset: 2px;
}
.modules-content table { min-width: 28rem; margin-bottom: 0; }
.modules-content td { vertical-align: top; overflow-wrap: anywhere; }
.modules-content th { white-space: normal; }
.modules-content code { color: #0a2c77; overflow-wrap: anywhere; }
.module-details { margin: .65rem 0; padding: .65rem .85rem;
  border: 1px solid #e8ecf0; border-radius: 4px; background: #fff; }
.module-details > summary { cursor: pointer; color: #1a2332; font-size: .88rem; font-weight: 600; }
.module-details .module-details { padding: .5rem; }
.modules-content pre { max-width: 100%; overflow-x: auto; }
.module-section .back-to-index { font-size: .8rem; }
@media (max-width: 768px) {
  .modules-content { padding-left: 1.25rem; padding-right: 1.25rem; }
  .module-details { padding: .5rem; }
}
'''


def esc(value):
    if isinstance(value, bool):
        value = 'true' if value else 'false'
    elif value is None:
        value = 'null'
    return escape(str(value))


def label(key):
    return str(key).replace('_', ' ').replace('-', ' ').capitalize()


def scalar(value):
    """Keep multiline code readable and all untrusted source text escaped."""
    if isinstance(value, str) and '\n' in value.rstrip('\n'):
        return '<pre><code>' + esc(value) + '</code></pre>'
    return esc(value)


def table(headers, rows, title):
    head = ''.join('<th scope="col">' + esc(h) + '</th>' for h in headers)
    body = ''.join('<tr>' + ''.join('<td>' + c + '</td>' for c in row) + '</tr>' for row in rows)
    return (f'<div class="module-table-scroll" tabindex="0" role="region" aria-label="{esc(title)}">'
            f'<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')


def details(title, content):
    return f'<details class="module-details"><summary>{esc(title)}</summary>{content}</details>'


def render(value, title='Definition'):
    """Render arbitrary module structures without a lossy key whitelist."""
    if isinstance(value, dict):
        if not value:
            return '<code>{}</code>'
        rows, children = [], []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                children.append(details(label(key), render(item, label(key))))
            else:
                rows.append((f'<code>{esc(key)}</code>', scalar(item)))
        return (table(['Property', 'Value'], rows, title) if rows else '') + ''.join(children)
    if isinstance(value, list):
        if not value:
            return '<code>[]</code>'
        if all(isinstance(item, dict) for item in value):
            keys = list(dict.fromkeys(key for item in value for key in item))
            # Requirements use their actual statement, level and verification fields.
            if len(keys) <= 4 and all(not isinstance(v, (list, dict)) for item in value for v in item.values()):
                return table([label(k) for k in keys],
                             [[scalar(item[k]) if k in item else '—' for k in keys] for item in value], title)
            return ''.join(details(str(item.get('name', item.get('id', item.get('class', f'Entry {i}')))),
                                   render(item, title)) for i, item in enumerate(value, 1))
        return '<ul>' + ''.join('<li>' + render(item, title) + '</li>' for item in value) + '</ul>'
    return scalar(value)


def build(repo, output, template):
    paths = sorted((repo / 'spec').glob('part-*/*.yaml'))
    if not paths:
        raise ValueError('No specification modules found')
    modules = []
    # Validate every source before writing any part of this page.
    for path in paths:
        raw = path.read_text(encoding='utf-8')
        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError as error:
            raise ValueError(f'{path.relative_to(repo)}: invalid YAML: {error}') from error
        if not isinstance(data, dict) or not data:
            raise ValueError(f'{path.relative_to(repo)}: expected a nonempty YAML mapping')
        title, description = MODULES.get(path.stem, (label(path.stem), 'Structured specification module.'))
        anchor = 'module-' + re.sub(r'[^a-z0-9-]+', '-', path.parent.name + '-' + path.stem.lower()).strip('-')
        modules.append((path, raw, data, title, description, anchor))

    index_rows = []
    for path, raw, data, title, description, anchor in modules:
        part = int(path.parent.name.split('-')[1])
        index_rows.append((f'Part {part}', f'<a href="#{anchor}">{esc(title)}</a>', esc(description)))
    content = ['<div class="content modules-content"><div class="modules-intro">',
               '<p>This reference presents the structured modules behind Parts 3–7. '
               'Expand definitions to inspect fields and constraints, or download the source YAML.</p>',
               '<p>Edition 2026a (draft). Requirement wording, levels and verification references '
               'are taken directly from the source files.</p></div>',
               '<h2 id="module-index">Module index</h2>',
               table(['Part', 'Module', 'Scope'], index_rows, 'Module index')]
    for path, raw, data, title, description, anchor in modules:
        part = int(path.parent.name.split('-')[1])
        relative = path.relative_to(repo).as_posix()
        download = Path('module-sources') / path.parent.name / path.name
        destination = output / download
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        content += [f'<section class="module-section" id="{anchor}">',
                    f'<h2>Part {part} — {esc(title)}</h2><p>{esc(description)}</p>',
                    f'<p class="module-meta"><a href="{esc(download.as_posix())}" download>Download YAML</a> · '
                    f'<a href="https://github.com/RocomFoundation/rocom-standard/blob/main/{esc(relative)}">View source on GitHub</a></p>']
        metadata = {k: v for k, v in data.items() if not isinstance(v, (dict, list))}
        if metadata:
            content.append(render(metadata, title + ' metadata'))
        for key, value in data.items():
            if not isinstance(value, (dict, list)):
                continue
            if key in ('principles', 'principals', 'requirements', 'data_classes', 'regulatory_mapping'):
                content.append(f'<h3>{esc(label(key))}</h3>' + render(value, label(key)))
            else:
                content.append(details(label(key), render(value, label(key))))
        content += [details('View complete source YAML', '<pre><code>' + esc(raw) + '</code></pre>'),
                    '<p class="back-to-index"><a href="#module-index">Back to module index</a></p></section>']
    content.append('</div>')
    html = template.read_text(encoding='utf-8')
    html = html.replace('</head>', '<style>' + STYLE + '</style></head>')
    html = html.replace('{{TITLE}}', 'Specification Modules').replace('{{CONTENT}}', ''.join(content))
    (output / 'modules.html').write_text(html, encoding='utf-8')


if __name__ == '__main__':
    build(*(Path(arg) for arg in sys.argv[1:]))
