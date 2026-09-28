#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="${1:-_site}"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="$REPO_DIR/build/template.html"
HOMEPAGE="$REPO_DIR/build/homepage.html"

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

# Translate internal doc links: .md → .html (for published site)
link_map = {
    'CONTRIBUTING.md': 'contributing.html',
    'GOVERNANCE.md': 'governance.html',
    'README.md': 'index.html',
}
for md_src, html_dst in link_map.items():
    body = body.replace(f'href="{md_src}"', f'href="{html_dst}"')

# Demote h1 → h2 in body (docheader already provides the page h1)
body = re.sub(r'<h1([^>]*)id="([^"]*)">([^<]*)</h1>', r'<h2\1 id="\2">\3</h2>', body)
body = re.sub(r'<h1([^>]*)>([^<]*)</h1>', r'<h2\1>\2</h2>', body)

# Build nested TOC from headings — use pandoc's actual id attributes
def build_toc(html_body):
    # Match headings with id attributes: <hN ... id="...">text</hN>
    headings = re.findall(r'<h([1-6])(?:\s[^>]*)?id="([^"]*)"(?:\s[^>]*)?>(.*?)</h\1>', html_body, re.DOTALL)
    # Also match headings without id (fallback)
    headings_no_id = re.findall(r'<h([1-6])(?:\s[^>]*)?>(.*?)</h\1>', html_body, re.DOTALL)
    if not headings and len(headings_no_id) < 2:
        return ''

    def clean_text(t):
        return re.sub(r'<[^>]+>', '', t).strip()

    # Build id map: for headings without id, generate slug
    id_set = set(h[1] for h in headings)
    def make_slug(t):
        s = re.sub(r'[^\w\s-]', '', t[:60]).lower()
        return '-'.join(s.split())

    if headings:
        items = [(int(l), hid, clean_text(txt)) for l, hid, txt in headings]
    else:
        items = [(int(l), make_slug(clean_text(txt)), clean_text(txt)) for l, txt in headings_no_id]

    if len(items) < 2:
        return ''

    base = min(lvl for lvl, _, _ in items)
    out = ['<details class="toc"><summary>Contents</summary>']
    cur_depth = -1
    prev_depth = -1
    for i, (lvl, hid, txt) in enumerate(items):
        depth = lvl - base
        while cur_depth < depth:
            out.append('<ul>')
            cur_depth += 1
        while cur_depth > depth:
            out.append('</li></ul>')
            cur_depth -= 1
            if depth >= 0:
                out.append('</li>')
        if i > 0 and depth == prev_depth:
            out.append('</li>')
        out.append(f'<li><a href="#{hid}">{txt}</a>')
        prev_depth = depth
    while cur_depth >= 0:
        out.append('</li></ul>')
        cur_depth -= 1
    out.append('</details>')
    return ''.join(out)

toc = build_toc(body)

# Doc-meta block
meta = ''
if status and lic:
    badge = "ADOPTED"
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
html = tpl.replace('{{TITLE}}', title).replace('{{CONTENT}}', toc + meta + '<div class="content">' + body + '</div>')
with open(os.path.join(output_dir, out), 'w') as f:
    f.write(html)
PYEOF
}

# Homepage — custom layout
if [ -f "$HOMEPAGE" ]; then
  cp "$HOMEPAGE" "$OUTPUT_DIR/index.html"
  echo "  index.html (homepage)"
else
  # Fallback: convert README
  [ -f "$REPO_DIR/README.md" ] && convert_md "$REPO_DIR/README.md" "index.html" && echo "  index.html"
fi

# Governance and contributing
[ -f "$REPO_DIR/GOVERNANCE.md" ]    && convert_md "$REPO_DIR/GOVERNANCE.md"    "governance.html"  && echo "  governance.html"
[ -f "$REPO_DIR/CONTRIBUTING.md" ]  && convert_md "$REPO_DIR/CONTRIBUTING.md"  "contributing.html" && echo "  contributing.html"

# Specification pages
[ -f "$REPO_DIR/spec/part-01-overview/OVERVIEW.md" ] && convert_md "$REPO_DIR/spec/part-01-overview/OVERVIEW.md" "part-01-overview.html" && echo "  part-01-overview.html"
[ -f "$REPO_DIR/spec/part-01-overview/ARM.md" ] && convert_md "$REPO_DIR/spec/part-01-overview/ARM.md" "part-01-arm.html" && echo "  part-01-arm.html"
[ -f "$REPO_DIR/spec/part-02-conformance/CONFORMANCE.md" ] && convert_md "$REPO_DIR/spec/part-02-conformance/CONFORMANCE.md" "part-02-conformance.html" && echo "  part-02-conformance.html"
[ -f "$REPO_DIR/spec/part-02-conformance/SERVICE-LEVELS.md" ] && convert_md "$REPO_DIR/spec/part-02-conformance/SERVICE-LEVELS.md" "part-02-service-levels.html" && echo "  part-02-service-levels.html"
[ -f "$REPO_DIR/spec/part-05-transport/TRANSPORT.md" ] && convert_md "$REPO_DIR/spec/part-05-transport/TRANSPORT.md" "part-05-transport.html" && echo "  part-05-transport.html"
[ -f "$REPO_DIR/spec/part-05-transport/PROFILE.md" ] && convert_md "$REPO_DIR/spec/part-05-transport/PROFILE.md" "part-05-transport.html" && echo "  part-05-transport.html"
[ -f "$REPO_DIR/docs/principles-and-architecture/PRINCIPLES.md" ] && convert_md "$REPO_DIR/docs/principles-and-architecture/PRINCIPLES.md" "principles.html" && echo "  principles.html"
[ -f "$REPO_DIR/docs/adopting-rocom/ADOPTING-ROCOM.md" ] && convert_md "$REPO_DIR/docs/adopting-rocom/ADOPTING-ROCOM.md" "adopting-rocom.html" && echo "  adopting-rocom.html"
[ -f "$REPO_DIR/docs/security-safety/SECURITY-SAFETY.md" ] && convert_md "$REPO_DIR/docs/security-safety/SECURITY-SAFETY.md" "security-safety.html" && echo "  security-safety.html"
[ -f "$REPO_DIR/docs/get-started/GET-STARTED.md" ] && convert_md "$REPO_DIR/docs/get-started/GET-STARTED.md" "get-started.html" && echo "  get-started.html"

# Modules page — structured YAML reference; invalid sources fail the build.
python3 "$REPO_DIR/build/render_modules.py" "$REPO_DIR" "$OUTPUT_DIR" "$TEMPLATE"
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
        sups[cells[0].lower()] = cells[4]
    return sups

sup_registry = parse_sup_registry(os.path.join(repo_dir, 'spec', 'cp-registry.md'))

def sup_status_badge(status_text):
    s = status_text.upper().strip()
    s = re.split(r'\s', s)[0] if s else ''
    if s == 'MERGED':
        return 'MERGED', 'badge-ratified'
    elif s == 'RATIFIED':
        return 'RATIFIED', 'badge-ratified'
    elif s == 'SUPERSEDED':
        return 'SUPERSEDED', 'badge-superseded'
    elif s == 'RESERVED':
        return 'RESERVED', 'badge-reserved'
    elif s == 'DRAFT':
        return 'DRAFT', 'badge-draft-status'
    elif s == 'ADOPTED':
        return 'ADOPTED', 'badge-ratified'
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
    # Strip all comment-header lines
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

    # Title from comment header or filename
    title = sn.replace('-', ' ').title()
    for line in raw.splitlines():
        if line.startswith('# Sup-') or line.startswith('# sup-'):
            title = line[2:].strip()
            break

    # Doc-meta
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
    s = re.split(r'\s', s)[0] if s else ''
    cls = 'badge-proposal'
    label = s
    if s == 'MERGED':
        cls = 'badge-ratified'
    elif s == 'RATIFIED':
        cls = 'badge-ratified'
    elif s == 'SUPERSEDED':
        cls = 'badge-superseded'
    elif s == 'RESERVED':
        cls = 'badge-reserved'
    elif s == 'DRAFT':
        cls = 'badge-draft-status'
    elif s == 'ADOPTED':
        cls = 'badge-ratified'
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

# Build registry_id -> filename mapping from actual CP files
cp_files = sorted(glob.glob(os.path.join(repo_dir, 'spec', 'cp-*.md')))
cp_id_to_file = {}
for cp_path in cp_files:
    bn = os.path.basename(cp_path).replace('.md', '')
    m_cp = re.match(r'(cp-\d+)', bn, re.I)
    if m_cp:
        cp_id_to_file[m_cp.group(1)] = bn

# Build supplement ID -> output filename mapping
sup_id_to_file = {}
for sp in glob.glob(os.path.join(repo_dir, 'spec', 'supplements', '*.md')):
    bn = os.path.basename(sp)
    if bn.startswith('archived-'):
        continue
    sn = bn.replace('.md', '')
    m_sup = re.match(r'(?:Sup-|sup-)(\d+)', sn)
    if m_sup:
        sup_id_to_file[f"sup-{m_sup.group(1)}"] = f"supplement-{sn}.html"

# Sort: PROPOSAL first, then all by date descending
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
<p>Each CP below shows its current status. A <span class="badge badge-proposal">PROPOSAL</span> is under review and is not yet normative text. A <span class="badge badge-ratified">MERGED</span> has been accepted and incorporated into the specification. <span class="badge badge-superseded">SUPERSEDED</span> has been replaced by a later change.</p>
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
    sup_status_upper = sup['status'].upper().strip()
    if sup_status_upper == 'RESERVED':
        link = html_esc(sup['id'])
    else:
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
    cp_id_match = re.match(r'(cp-\d+)', bn, re.I)
    cp_status = 'PROPOSAL'
    if cp_id_match:
        cp_id = cp_id_match.group(1).upper()
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
# Count pages
page_count=$(find "$OUTPUT_DIR" -name "*.html" | wc -l)
echo "Done: $page_count pages in $OUTPUT_DIR/"
