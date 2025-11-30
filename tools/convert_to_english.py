#!/usr/bin/env python3
"""
Safe docs-only American→Irish (UK-style) English spelling converter.
- Processes .md and .txt files under the workspace.
- Skips content inside fenced code blocks (```), and skips inline code spans (`...`).
- Default mode is dry-run; use `--apply` to write changes.

Usage:
    python tools/convert_to_english.py --dry-run
    python tools/convert_to_english.py --apply

This script is conservative: it only modifies text outside code fences and inline code spans.
"""
import re
import sys
from pathlib import Path

# mapping from US spelling regex -> replacement
REPLACEMENTS = [
    (r"\boptimi(s|z)e(d|r|s|ation|ing)?\b", lambda m: m.group(0).replace('z', 's')),
    (r"\bcustomi(s|z)e(d|r|s|ation|ing)?\b", lambda m: m.group(0).replace('z', 's')),
    (r"\bbehavio(u)?r(s|al|ally)?\b", None),
]
# Because regex for behaviour/behavior needs explicit handling, provide explicit list
EXACT_REPLACEMENTS = {
    # US -> UK
    'behavioral': 'behavioural',
    'behaviorally': 'behaviourally',
    'behavior': 'behaviour',
    'behaviors': 'behaviours',
    'analyze': 'analyse',
    'analyzes': 'analyses',
    'analyzed': 'analysed',
    'analyzing': 'analysing',
    'analyser': 'analyser',
    'analyzers': 'analysers',
    'optimization': 'optimisation',
    'optimizations': 'optimisations',
    'optimize': 'optimise',
    'optimizes': 'optimises',
    'optimized': 'optimised',
    'optimizing': 'optimising',
    'customization': 'customisation',
    'customizations': 'customisations',
    'customize': 'customise',
    'customizes': 'customises',
    'customized': 'customised',
    'customizing': 'customising',
    'color': 'colour',
    'colors': 'colours',
    'color-coded': 'colour-coded',
    'coloring': 'colouring',
    'organize': 'organise',
    'organizes': 'organises',
    'organized': 'organised',
    'organizing': 'organising',
    'prioritize': 'prioritise',
    'prioritizes': 'prioritises',
    'prioritized': 'prioritised',
    'prioritizing': 'prioritising',
    'center': 'centre',
    'centers': 'centres',
    'centered': 'centred',
    'modeling': 'modelling',
    'modeler': 'modeller',
    'meter': 'metre',
    'meters': 'metres',
    'localization': 'localisation',
    'localize': 'localise',
}

# Build regex for exact word replacement (case-sensitive preserved)
WORD_RE = re.compile(r"\b(" + "|".join(re.escape(k) for k in EXACT_REPLACEMENTS.keys()) + r")\b")

def replace_outside_code(text):
    # Split on fenced code blocks ``` (preserve fence markers)
    parts = re.split(r'(```[^\n]*\n|```\n)', text)
    # parts: alternating segments; we will only modify even-indexed content (outside code fence markers and blocks)
    out = []
    i = 0
    while i < len(parts):
        segment = parts[i]
        if segment.startswith('```'):
            # it's a fence marker followed by a block in next part
            out.append(segment)
            i += 1
            if i < len(parts):
                out.append(parts[i])  # code block content, unchanged
                i += 1
        else:
            # This is outside code; but may contain inline code spans `...` which we should skip
            new_seg = ''
            # Split by inline code spans
            chunks = re.split(r'(`[^`]*`)', segment)
            for j, ch in enumerate(chunks):
                if ch.startswith('`') and ch.endswith('`'):
                    new_seg += ch
                else:
                    # perform word replacements on this chunk
                    new_chunk = WORD_RE.sub(lambda m: EXACT_REPLACEMENTS[m.group(0)], ch)
                    # Also handle case-insensitive common variants (lowercase only mapping above)
                    # Preserve case for first letter
                    def case_preserve_replace(match):
                        key = match.group(0)
                        repl = EXACT_REPLACEMENTS.get(key.lower())
                        if not repl:
                            return key
                        if key.isupper():
                            return repl.upper()
                        if key[0].isupper():
                            return repl.capitalize()
                        return repl
                    new_chunk = re.sub(r"\b(" + "|".join(re.escape(k) for k in EXACT_REPLACEMENTS.keys()) + r")\b", case_preserve_replace, ch)
                    new_seg += new_chunk
            out.append(new_seg)
            i += 1
    return ''.join(out)


def process_file(path: Path, apply: bool=False):
    text = path.read_text(encoding='utf-8')
    new_text = replace_outside_code(text)
    if new_text != text:
        if apply:
            path.write_text(new_text, encoding='utf-8')
        return True, new_text
    return False, text


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='Write changes')
    parser.add_argument('--root', default='.', help='Repository root')
    args = parser.parse_args()

    root = Path(args.root)
    files = list(root.rglob('*.md')) + list(root.rglob('*.txt'))
    changed = []
    for f in files:
        # skip .git, node_modules, and common virtualenv directories
        if any(p in f.parts for p in ('.git', 'node_modules', '.venv', 'venv')):
            continue
        ok, _ = process_file(f, apply=args.apply)
        if ok:
            changed.append(str(f))
    print('Dry-run:' if not args.apply else 'Applied changes:')
    print(f'Files scanned: {len(files)}')
    print(f'Files changed: {len(changed)}')
    for c in changed:
        print(' -', c)

if __name__ == '__main__':
    main()
