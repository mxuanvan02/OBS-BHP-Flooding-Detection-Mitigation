from pathlib import Path

src = Path('docx_work/final_extracted.txt')
text = src.read_text(encoding='utf-8')
terms = [
    'direct-BHP', 'seed', 'native', 'artifact', 'gate', 'pipeline', 'topology',
    'scenario', 'Detector online', 'prediction/action linkage', 'Grouped holdout',
    'Raw fold predictions', 'uncertainty', 'synthetic', 'direct-only', 'admitted',
    'control', 'guard', 'token', 'payload', 'fold', 'benchmark', 'burst',
]
out = []
for term in terms:
    hits = [line for line in text.splitlines() if term.casefold() in line.casefold()]
    out.append(f'## {term}: {len(hits)}')
    out.extend(hits)
Path('docx_work/terminology_audit.txt').write_text('\n'.join(out) + '\n', encoding='utf-8')
print('wrote docx_work/terminology_audit.txt')
