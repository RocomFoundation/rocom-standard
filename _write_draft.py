#!/usr/bin/env python3
"""Write control-plane service levels draft to spec dir."""
from pathlib import Path

dst = Path(__file__).parent / 'spec' / 'part-02-conformance' / 'control-plane-service-levels-DRAFT.md'
dst.parent.mkdir(parents=True, exist_ok=True)

# Read content from /tmp/cpl_draft.md (pasted by user) or fall back to inline
src = Path('/tmp/cpl_draft.md')
if src.exists() and src.stat().st_size > 1000:
    content = src.read_text()
else:
    raise SystemExit('Content not found at /tmp/cpl_draft.md — paste it there first')

dst.write_text(content)
print(f'Wrote {len(content)} bytes to {dst}')
