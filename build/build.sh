#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="${1:-_site}"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="$REPO_DIR/build/template.html"

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

echo "=== Building Rocom spec site ==="

# Convert a single MD file to HTML using template
convert_md() {
  python3 - "$REPO_DIR" "$1" "$2" "$OUTPUT_DIR" "$TEMPLATE" << 'PYEOF'
import sys, subprocess, re, os

repo_dir, src, out, output_dir, template = sys.argv[1:]

with open(src) as f:
    raw = f.read()

# Title from first # heading (skip comment lines like # === or # FILE:)
title = os.path.basename(src).replace('.md', '')
for line in raw.splitlines():
    if line.startswith('# ') and not line.startswith('# ===') and not line.startswith('# FILE:'):
        title = line[2:].strip()
        break

# Status/license from comment headers
status = ''
lic = ''
for line in raw.splitlines():
    if line.startswith('# Status:'):
        status = line[len('# Status:'):].strip()
    if line.startswith('# License:'):
        lic = line[len('# License:'):].strip()

# Strip comment-header lines, pandoc convert
clean = raw
for pat in [r'^# FILE:.*', r'^# ===.*', r'^# Status:.*', r'^# License:.*', r'^# Scope:.*', r'^# NOTE:.*']:
    clean = re.sub(pat, '', clean, flags=re.M)
clean = re.sub(r'\n{3,}', '\n\n', clean)
try:
    result = subprocess.run(
        ['pandoc', '-f', 'markdown', '-t', 'html', '--wrap=none'],
        input=clean, capture_output=True, text=True, check=True
    )
    body = result.stdout
except Exception:
    body = clean.replace('\n', '<br>')

# Build nested TOC from headings (DICOM-style)
def build_toc(html_body):
    headings = re.findall(r'<h([1-6])(?:\s[^>]*)?>(.*?)</h\1>', html_body, re.DOTALL)
    if len(headings) < 2:
        return ''
    def clean_text(t):
        return re.sub(r'<[^>]+>', '', t).strip()
    def make_slug(t):
        s = re.sub(r'[^\w\s-]', '', t[:60]).lower()
        return '-'.join(s.split())
    # Compute depth relative to shallowest heading
    levels = [int(l) for l, _ in headings]
    base = min(levels)
    items = [(int(lvl) - base, make_slug(clean_text(txt)), clean_text(txt)) for lvl, txt in headings]
    # Simple renderer: track current depth, emit open/close as needed
    out = ['<div class="toc"><div class="toc-title">Contents</div>']
    cur_depth = -1
    prev_depth = -1
    for i, (depth, slug, txt) in enumerate(items):
        # Going deeper: open new <ul> for each level
        while cur_depth < depth:
            out.append('<ul>')
            cur_depth += 1
        # Going shallower: close </li></ul> for each level, then close parent <li>
        while cur_depth > depth:
            out.append('</li></ul>')
            cur_depth -= 1
            if depth >= 0:
                out.append('</li>')
        # Same level as previous: close previous <li>
        if i > 0 and depth == prev_depth:
            out.append('</li>')
        out.append(f'<li><a href="#{slug}">{txt}</a>')
        prev_depth = depth
    # Close remaining open lists
    while cur_depth >= 0:
        out.append('</li></ul>')
        cur_depth -= 1
    out.append('</div>')
    return ''.join(out)

toc = build_toc(body)

# Doc-meta block
meta = ''
if status and lic:
    badge = 'DRAFT'
    cls = 'badge-draft'
    if any(w in status.lower() for w in ('final', 'published')):
        badge = 'FINAL'
        cls = 'badge-final'
    meta = (
        f"<div class='doc-meta'>"
        f"<strong>Document:</strong> {title} &nbsp;"
        f"<span class='badge {cls}'>{badge}</span>"
        f"<br><strong>Status:</strong> {status}"
        f"<br><strong>License:</strong> {lic}"
        f"</div>"
    )

# Read template and substitute
with open(template) as f:
    tpl = f.read()

content = meta + toc + '<div class="content">' + body + '</div>'
html = tpl.replace('{{TITLE}}', title).replace('{{CONTENT}}', content)

with open(os.path.join(output_dir, out), 'w') as f:
    f.write(html)
PYEOF
}

# Index
[ -f "$REPO_DIR/README.md" ]      && convert_md "$REPO_DIR/README.md"      "index.html"       && echo "  index.html"
[ -f "$REPO_DIR/GOVERNANCE.md" ]    && convert_md "$REPO_DIR/GOVERNANCE.md"    "governance.html"  && echo "  governance.html"
[ -f "$REPO_DIR/CONTRIBUTING.md" ]  && convert_md "$REPO_DIR/CONTRIBUTING.md"  "contributing.html" && echo "  contributing.html"

# Spec parts
[ -f "$REPO_DIR/spec/part-01-overview/OVERVIEW.md" ]     && convert_md "$REPO_DIR/spec/part-01-overview/OVERVIEW.md"     "part-01-overview.html"     && echo "  part-01-overview.html"
[ -f "$REPO_DIR/spec/part-01-overview/ARM.md" ]          && convert_md "$REPO_DIR/spec/part-01-overview/ARM.md"          "part-01-arm.html"            && echo "  part-01-arm.html"
[ -f "$REPO_DIR/spec/part-02-conformance/CONFORMANCE.md" ] && convert_md "$REPO_DIR/spec/part-02-conformance/CONFORMANCE.md" "part-02-conformance.html" && echo "  part-02-conformance.html"
[ -f "$REPO_DIR/spec/part-05-transport/PROFILE.md" ]       && convert_md "$REPO_DIR/spec/part-05-transport/PROFILE.md"       "part-05-transport.html"       && echo "  part-05-transport.html"

# Principles & Architecture
[ -f "$REPO_DIR/docs/principles-and-architecture/PRINCIPLES.md" ] && convert_md "$REPO_DIR/docs/principles-and-architecture/PRINCIPLES.md" "principles.html" && echo "  principles.html"

# YAML modules page — render as formatted requirement tables
python3 - "$REPO_DIR" "$OUTPUT_DIR" "$TEMPLATE" << 'PYEOF'
import sys, os, glob, re, subprocess
repo_dir, output_dir, template = sys.argv[1:]

def html_esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def render_principles(principles):
    if not principles:
        return ''
    rows = ''
    for p in principles:
        pid = html_esc(p.get('id', ''))
        stmt = html_esc(p.get('statement', ''))
        rows += f'<tr><td><code>{pid}</code></td><td>{stmt}</td></tr>\n'
    return f'<table><thead><tr><th style="width:140px">ID</th><th>Principle</th></tr></thead><tbody>\n{rows}</tbody></table>'

def render_requirements(reqs):
    if not reqs:
        return ''
    # Group by level
    by_level = {}
    for r in reqs:
        lvl = r.get('level', 'unknown')
        by_level.setdefault(lvl, []).append(r)
    level_names = {'L1': 'L1 — Pilot / Lab', 'L2': 'L2 — Production Single Site', 'L3': 'L3 — Production Multi-Site', 'L1+': 'All Levels'}
    sections = ''
    for lvl in ['L1', 'L2', 'L3', 'L1+']:
        items = by_level.get(lvl, [])
        if not items:
            continue
        rows = ''
        for r in items:
            rid = html_esc(r.get('id', ''))
            stmt = html_esc(r.get('statement', ''))
            ver = html_esc(r.get('verification', ''))
            rows += f'<tr><td><code>{rid}</code></td><td>{stmt}</td><td><small>{ver}</small></td></tr>\n'
        lbl = level_names.get(lvl, lvl)
        sections += f'<h3>{lbl}</h3>\n<table><thead><tr><th style="width:110px">ID</th><th>Requirement</th><th style="width:200px">Verification</th></tr></thead><tbody>\n{rows}</tbody></table>\n'
    return sections

content = "<div class='doc-meta'><strong>Specification Modules</strong> — YAML modules rendered as requirement tables.</div><div class='content'>"
for yp in sorted(glob.glob(os.path.join(repo_dir, 'spec', 'part-*', '*.yaml'))):
    yn = os.path.basename(yp)
    lp = os.path.basename(os.path.dirname(yp))
    with open(yp) as f:
        raw = f.read()
    # Strip comment headers for pandoc
    clean = raw
    for pat in [r'^# FILE:.*', r'^# ===.*', r'^# Status:.*', r'^# License:.*', r'^# Scope:.*', r'^# NOTE:.*']:
        clean = re.sub(pat, '', clean, flags=re.M)
    # Try to render intro text via pandoc (full content, not truncated)
    intro = ''
    try:
        result = subprocess.run(['pandoc', '-f', 'markdown', '-t', 'html', '--wrap=none'],
            input=clean, capture_output=True, text=True, check=True)
        intro = result.stdout.strip()
    except:
        pass
    # Parse YAML for tables — fail loudly on parse errors
    import yaml
    try:
        data = yaml.safe_load(raw)
        if data is None:
            print(f"  WARNING: {yn} parsed as empty YAML — no tables rendered")
            data = {}
    except yaml.YAMLError as e:
        print(f"  ERROR: {yn} YAML parse failed: {e}")
        data = {}
    content += f'<h2>{html_esc(lp)}: {html_esc(yn)}</h2>\n'
    if intro:
        content += intro + '\n'
    content += render_principles(data.get('principals', data.get('principles', [])))
    content += render_requirements(data.get('requirements', []))
    # Data classes table
    if data.get('data_classes'):
        rows = ''
        for dc in data['data_classes']:
            c = html_esc(dc.get('class', ''))
            d = html_esc(dc.get('definition', ''))
            pd = html_esc(dc.get('personal_data', ''))
            rows += f'<tr><td><strong>{c}</strong></td><td>{d}</td><td>{pd}</td></tr>\n'
        content += f'<h3>Data Classes</h3>\n<table><thead><tr><th>Class</th><th>Definition</th><th>Personal Data?</th></tr></thead><tbody>\n{rows}</tbody></table>\n'
    # Regulatory mapping
    if data.get('regulatory_mapping'):
        rows = ''
        for rm in data['regulatory_mapping']:
            reg = html_esc(rm.get('regime', ''))
            rel = html_esc(rm.get('relevance', ''))
            rows += f'<tr><td><strong>{reg}</strong></td><td>{rel}</td></tr>\n'
        content += f'<h3>Regulatory Mapping</h3>\n<table><thead><tr><th>Regime</th><th>Relevance</th></tr></thead><tbody>\n{rows}</tbody></table>\n'
    content += '<hr/>\n'
content += '</div>'

with open(template) as f:
    tpl = f.read()
html = tpl.replace('{{TITLE}}', 'Specification Modules').replace('{{CONTENT}}', content)
with open(os.path.join(output_dir, 'modules.html'), 'w') as f:
    f.write(html)
PYEOF
echo "  modules.html"

# Supplements page — each gets its own page, plus an index
python3 - "$REPO_DIR" "$OUTPUT_DIR" "$TEMPLATE" << 'PYEOF'
import sys, os, glob, re, subprocess
repo_dir, output_dir, template = sys.argv[1:]

supps = sorted([s for s in glob.glob(os.path.join(repo_dir, 'spec', 'supplements', '*.md'))
                      if not os.path.basename(s).startswith('archived-')])

# Build registry-based status lookup for supplements
def parse_sup_registry(path):
    sups = {}
    if not os.path.exists(path):
        return sups
    with open(path) as f:
        text = f.read()
    in_section = False
    for line in text.splitlines():
        if line.strip() == '## Supplements':
            in_section = True
            continue
        elif line.startswith('## '):
            in_section = False
            continue
        if not in_section:
            continue
        m = re.match(r'^\|(.*)\|$', line.strip())
        if not m:
            continue
        cells = [c.strip() for c in m.group(1).split('|')]
        if len(cells) < 5 or cells[0] in ('Sup', '-----'):
            continue
        sups[cells[0].lower()] = cells[4]  # status column
    return sups

sup_registry = parse_sup_registry(os.path.join(repo_dir, 'spec', 'cp-registry.md'))

def sup_status_badge(status_text):
    s = status_text.upper().strip()
    # Normalize: MERGED (Edition 2026a draft) -> MERGED
    s = re.split(r'\s', s)[0] if s else ''
    if s in ('RATIFIED', 'MERGED'):
        return 'RATIFIED', 'badge-ratified'
    elif s == 'SUPERSEDED':
        return 'SUPERSEDED', 'badge-superseded'
    elif s == 'RESERVED':
        return 'RESERVED', 'badge-reserved'
    elif s in ('DRAFT',):
        return 'DRAFT', 'badge-draft-status'
    elif s == 'PROPOSAL':
        return 'PROPOSAL', 'badge-proposal'
    elif s in ('FINAL', 'PUBLISHED'):
        return 'FINAL', 'badge-final'
    return s, 'badge-draft'

# Build index page
content = "<div class='doc-meta'><strong>Supplementary Documents</strong></div><div class='content'>"
if supps:
    content += '<ul>'
    for sp in supps:
        sn = os.path.basename(sp).replace('.md', '')
        content += f'<li><a href="supplement-{sn}.html">{sn}</a></li>'
    content += '</ul>'
else:
    content += '<p>No supplementary documents yet.</p>'
content += '</div>'

with open(template) as f:
    tpl = f.read()
html = tpl.replace('{{TITLE}}', 'Supplements').replace('{{CONTENT}}', content)
with open(os.path.join(output_dir, 'supplements.html'), 'w') as f:
    f.write(html)

# Build individual pages
for sp in supps:
    sn = os.path.basename(sp).replace('.md', '')
    with open(sp) as f:
        raw = f.read()
    # Strip all comment-header lines (# FILE:, # ===, # Sup-xxx, # Status:, # License:, # Scope:, # NOTE:, and indented # lines)
    clean = raw
    for pat in [r'^# FILE:.*', r'^# ===.*', r'^# Status:.*', r'^# License:.*', r'^# Scope:.*', r'^# NOTE:.*', r'^#[A-Z]{3}-\d+.*', r'^#\s+.+']:
        clean = re.sub(pat, '', clean, flags=re.M)
    clean = re.sub(r'\n{3,}', '\n\n', clean)

    # Extract metadata from comment headers
    file_status = ''
    file_lic = ''
    for line in raw.splitlines():
        if line.startswith('# Status:'): file_status = line[len('# Status:'):].strip()
        if line.startswith('# License:'): file_lic = line[len('# License:'):].strip()

    # Prefer registry status over file header
    sup_id_match = re.match(r'(?:Sup-|sup-)(\d+)', sn)
    sup_id = f"sup-{sup_id_match.group(1)}" if sup_id_match else sn.lower()
    status = sup_registry.get(sup_id, file_status)
    lic = file_lic

    # Title from comment header (# Sup-001 ...) or filename with dashes replaced
    title = sn.replace('-', ' ').title()
    for line in raw.splitlines():
        if line.startswith('# Sup-') or line.startswith('# sup-'):
            title = line[2:].strip()
            break

    # Doc-meta — badge from status text (MERGED/DRAFT/PROPOSAL)
    meta = ''
    if status and lic:
        badge, cls = sup_status_badge(status)
        meta = (
            f"<div class='doc-meta'>"
            f"<strong>Document:</strong> {title} &nbsp;"
            f"<span class='badge {cls}'>{badge}</span>"
            f"<br><strong>Status:</strong> {status}"
            f"<br><strong>License:</strong> {lic}"
            f"</div>"
        )

    # Convert
    try:
        result = subprocess.run(
        ['pandoc', '-f', 'markdown', '-t', 'html', '--wrap=none'],
            input=clean, capture_output=True, text=True, check=True
        )
        body = result.stdout
    except Exception:
        body = '<pre>' + clean.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') + '</pre>'

    full_content = meta + '<div class="content">' + body + '</div>'
    with open(template) as f:
        tpl = f.read()
    html = tpl.replace('{{TITLE}}', title).replace('{{CONTENT}}', full_content)
    with open(os.path.join(output_dir, f'supplement-{sn}.html'), 'w') as f:
        f.write(html)
PYEOF
echo "  supplements.html"

# Changes page — parse cp-registry.md, render CP/Sup table + explanation, + individual CP pages
python3 - "$REPO_DIR" "$OUTPUT_DIR" "$TEMPLATE" << 'PYEOF'
import sys, os, re, subprocess, glob

repo_dir, output_dir, template = sys.argv[1:]

def html_esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def status_badge(status):
    s = status.upper().strip()
    cls = 'badge-proposal'
    label = s
    if s in ('RATIFIED', 'MERGED'):
        cls = 'badge-ratified'
        label = 'RATIFIED'
    elif s == 'SUPERSEDED':
        cls = 'badge-superseded'
    elif s == 'RESERVED':
        cls = 'badge-reserved'
    elif s in ('DRAFT',):
        cls = 'badge-draft-status'
    elif s == 'PROPOSAL':
        cls = 'badge-proposal'
    return f'<span class="badge {cls}">{label}</span>', cls

def parse_registry(path):
    cps = []
    sups = []
    if not os.path.exists(path):
        return cps, sups
    with open(path) as f:
        text = f.read()
    in_section = None
    for line in text.splitlines():
        if line.strip() == '## Correction Proposals':
            in_section = 'cp'
            continue
        elif line.strip() == '## Supplements':
            in_section = 'sup'
            continue
        elif line.startswith('## '):
            in_section = None
            continue
        m = re.match(r'^\|(.*)\|$', line.strip())
        if not m or in_section is None:
            continue
        cells = [c.strip() for c in m.group(1).split('|')]
        if len(cells) < 5 or cells[0] in ('CP', 'Sup', '----', '-----'):
            continue
        if in_section == 'cp':
            cps.append({
                'id': cells[0], 'title': cells[1], 'commit': cells[2],
                'date': cells[3], 'status': cells[4],
                'repo': cells[5] if len(cells) > 5 else ''
            })
        elif in_section == 'sup':
            sups.append({
                'id': cells[0], 'title': cells[1], 'commit': cells[2],
                'date': cells[3], 'status': cells[4]
            })
    return cps, sups

def infer_part(title):
    t = title.lower()
    if any(k in t for k in ['architecture', 'overview', 'scope', 'arm', 'reference model']):
        return 'Part 1'
    if any(k in t for k in ['conformance']):
        return 'Part 2'
    if any(k in t for k in ['information model', 'agent identity', 'data model', 'costmodel', 'cost']):
        return 'Part 3'
    if any(k in t for k in ['service', 'contract', 'orchestrator', 'api', 'interface']):
        return 'Part 4'
    if any(k in t for k in ['transport', 'vda', 'profile', 'binding']):
        return 'Part 5'
    if any(k in t for k in ['security']):
        return 'Part 6'
    if any(k in t for k in ['data governance', 'governance', 'privacy']):
        return 'Part 7'
    return 'General'

# Parse registry
cps, sups = parse_registry(os.path.join(repo_dir, 'spec', 'cp-registry.md'))

# Build supplement ID -> output filename mapping
sup_id_to_file = {}
for sp in glob.glob(os.path.join(repo_dir, 'spec', 'supplements', '*.md')):
    bn = os.path.basename(sp)
    if bn.startswith('archived-'):
        continue
    sn = bn.replace('.md', '')
    # Extract sup ID (e.g., "Sup-001-Orchestrator..." -> "sup-001")
    m_sup = re.match(r'(?:Sup-|sup-)(\d+)', sn)
    if m_sup:
        sup_id_to_file[f"sup-{m_sup.group(1)}"] = f"supplement-{sn}.html"

# Build registry_id -> filename mapping from actual CP files
cp_files = sorted(glob.glob(os.path.join(repo_dir, 'spec', 'cp-*.md')))
cp_id_to_file = {}
for cp_path in cp_files:
    bn = os.path.basename(cp_path).replace('.md', '')
    m_cp = re.match(r'(cp-\d+)', bn, re.I)
    if m_cp:
        cp_id_to_file[m_cp.group(1)] = bn

# Sort: PROPOSAL first, then all by date descending
def cp_sort_key(x):
    s = x['status'].upper()
    if s == 'PROPOSAL':
        return (0, x['date'])
    return (1, x['date'])
cps_sorted = sorted(cps, key=cp_sort_key, reverse=True)
# Fix: PROPOSAL should be first regardless, then rest by date desc
cps_proposal = [x for x in cps if x['status'].upper() == 'PROPOSAL']
cps_other = [x for x in cps if x['status'].upper() != 'PROPOSAL']
cps_other.sort(key=lambda x: x['date'], reverse=True)
cps_sorted = cps_proposal + cps_other

# Build changes page
content = """<div class="content">
<h2>What Is a Change Record?</h2>
<p>The Rocom specification evolves through a structured change process with three mechanisms, modeled after standards bodies like DICOM and IEC:</p>
<ul>
<li><strong>Editions</strong> — Major revisions that produce a new version of the specification (e.g., Edition 2026a, Edition 2027a). Editions are published after broad review and may contain breaking changes.</li>
<li><strong>Supplements</strong> — Additions or significant modifications between editions. Supplements add new normative content, annexes, or profiles without replacing existing text. They are incorporated into the next edition.</li>
<li><strong>Correction Proposals (CPs)</strong> — Targeted fixes, clarifications, or small improvements to an existing edition. Each CP addresses a single issue and is tracked through proposal, review, and ratification.</li>
</ul>

<h2>Correction Proposals</h2>
<p>Each CP below shows its current status. A <span class="badge badge-proposal">PROPOSAL</span> is under review and is not yet normative text. A <span class="badge badge-ratified">RATIFIED</span> has been accepted and incorporated into the specification. <span class="badge badge-superseded">SUPERSEDED</span> has been replaced by a later change.</p>
<table>
<thead><tr><th style="width:70px">CP</th><th>Title</th><th style="width:90px">Status</th><th style="width:90px">Date</th><th style="width:80px">Part</th></tr></thead>
<tbody>
"""

for cp in cps_sorted:
    badge, _ = status_badge(cp['status'])
    part = infer_part(cp['title'])
    cp_slug = cp_id_to_file.get(cp['id'].lower())
    if cp_slug:
        cp_id_cell = f'<a href="cp-{cp_slug}.html">{html_esc(cp["id"])}</a>'
    else:
        cp_id_cell = html_esc(cp['id'])
    content += f'<tr><td>{cp_id_cell}</td><td>{html_esc(cp["title"])}</td><td>{badge}</td><td>{html_esc(cp["date"])}</td><td>{html_esc(part)}</td></tr>\n'

content += """</tbody></table>

<h2>Supplements</h2>
<table>
<thead><tr><th style="width:80px">Sup</th><th>Title</th><th style="width:90px">Status</th><th style="width:90px">Date</th></tr></thead>
<tbody>
"""

for sup in sups:
    badge, _ = status_badge(sup['status'])
    sup_key = sup['id'].lower()
    sup_filename = sup_id_to_file.get(sup_key, f"supplement-{sup_key}.html")
    link = f'<a href="{sup_filename}">{html_esc(sup["id"])}</a>'
    content += f'<tr><td>{link}</td><td>{html_esc(sup["title"])}</td><td>{badge}</td><td>{html_esc(sup["date"])}</td></tr>\n'

content += '</tbody></table></div>'

with open(template) as f:
    tpl = f.read()
html = tpl.replace('{{TITLE}}', 'Changes — Correction Proposals &amp; Supplements').replace('{{CONTENT}}', content)
with open(os.path.join(output_dir, 'changes.html'), 'w') as f:
    f.write(html)

# Individual CP pages — status from registry, not file header
for cp_path in cp_files:
    bn = os.path.basename(cp_path).replace('.md', '')
    with open(cp_path) as f:
        raw = f.read()
    # Get status from registry — match by CP-ID (e.g., "CP-007")
    cp_id_match = re.match(r'(cp-\d+)', bn, re.I)
    cp_status = 'PROPOSAL'  # fallback
    if cp_id_match:
        cp_id = cp_id_match.group(1).upper()  # "CP-007"
        for cp_entry in cps:
            if cp_entry['id'] == cp_id:
                cp_status = cp_entry['status']
                break
    title = bn
    for line in raw.splitlines():
        if line.startswith('# '):
            title = line[2:].strip()
            break
    badge, _ = status_badge(cp_status)
    status_meta = f"<div class='doc-meta'><strong>Correction Proposal: {html_esc(bn)}</strong> &nbsp; {badge}</div>"
    clean = re.sub(r'^\*\*Status:\*\*.*$', '', raw, flags=re.M)
    clean = re.sub(r'\n{3,}', '\n\n', clean)
    try:
        result = subprocess.run(
            ['pandoc', '-f', 'markdown', '-t', 'html', '--wrap=none'],
            input=clean, capture_output=True, text=True, check=True
        )
        body = result.stdout
    except Exception:
        body = '<pre>' + html_esc(clean) + '</pre>'
    full_content = status_meta + '<div class="content">' + body + '</div>'
    with open(template) as f:
        tpl = f.read()
    page_html = tpl.replace('{{TITLE}}', title).replace('{{CONTENT}}', full_content)
    with open(os.path.join(output_dir, f'cp-{bn}.html'), 'w') as f:
        f.write(page_html)

PYEOF
echo "  changes.html"

# Static brand assets
if [ -d "$REPO_DIR/build/assets" ]; then
  cp -R "$REPO_DIR/build/assets" "$OUTPUT_DIR/assets"
  echo "  assets (brand files)"
fi

# CNAME for custom domain
if [ -f "$REPO_DIR/build/CNAME" ]; then
  cp "$REPO_DIR/build/CNAME" "$OUTPUT_DIR/CNAME"
  echo "  CNAME (custom domain)"
fi

echo ""
echo "Done: $(find "$OUTPUT_DIR" -name '*.html' | wc -l) pages in $OUTPUT_DIR/"
