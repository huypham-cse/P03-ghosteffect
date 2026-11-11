#!/usr/bin/env python3
"""Count source-level LaTeX readability issues; PDF reading is still required.

Usage: python3 team/readability_count.py [--strict] [--json] FILE_OR_DIR [...]
Use --scope paper for the combined body limits (15 para / 30 emph).
Default limits apply to one contributor's combined files (5 / 10).
"""
import argparse
import json
from pathlib import Path
import re
import sys


def strip_comments(source):
    return '\n'.join(
        re.split(r'(?<!\\)%', line, maxsplit=1)[0] for line in source.splitlines())


def prose(source):
    text = strip_comments(source)
    # Ignore code, tabular material, TikZ and display math. Inline math is one
    # placeholder word so formula punctuation does not create sentence breaks.
    text = re.sub(r'\\begin\{(verbatim|lstlisting|tabular\*?|tikzpicture|equation\*?|align\*?)\}.*?'
                  r'\\end\{\1\}', ' ', text, flags=re.S)
    text = re.sub(r'\$\$.*?\$\$|\\\[.*?\\\]', ' ', text, flags=re.S)
    text = re.sub(r'(?<!\\)\$(?:\\.|[^$])*?\$|\\\(.*?\\\)', ' FORMULA ', text, flags=re.S)
    text = re.sub(r'\\(?:label|input|include|bibliography|bibliographystyle)\{[^{}]*\}', ' ', text)
    text = re.sub(r'\\(?:cite\w*|ref|eqref|Sref)(?:\[[^\]]*\])?\{[^{}]*\}', ' REFERENCE ', text)
    text = re.sub(r'\\(?:section|subsection|subsubsection)\*?\{[^{}]*\}', '\n\n', text)
    text = re.sub(r'\\para\{', '\n\n{', text)
    text = re.sub(r'\\(?:begin|end)\{[^{}]*\}', ' ', text)
    text = re.sub(r'\\(?:smallskip|noindent|centering|footnotesize|scriptsize)\b', ' ', text)
    # Retain inline result macros as a word, and retain text arguments of
    # emphasis/bold/para, rather than counting command names as prose words.
    text = re.sub(r'\\(?:emph|textbf|textit|texttt|textrm|textsf|mathrm|text|mbox|ensuremath)(?=\{)', '', text)
    text = re.sub(r'\\[A-Za-z]+', ' RESULT ', text)
    text = re.sub(r'\\[^A-Za-z\s]', ' ', text)
    return text.replace('{', '').replace('}', '').replace('~', ' ')


def sentences(paragraph):
    protected = re.sub(r'\b(?:e\.g\.|i\.e\.|et al\.|Fig\.|Eq\.|vs\.|Dr\.|Prof\.)',
                       lambda m: m.group().replace('.', '\u2024'), paragraph)
    protected = re.sub(r'(?<=\d)\.(?=\d)', '\u2024', protected)
    return [s.replace('\u2024', '.').strip()
            for s in re.split(r'[.!?]+(?:\s+|$)', protected) if s.strip()]


def count_file(path):
    source = strip_comments(Path(path).read_text(encoding='utf-8-sig'))
    paragraphs = [p for p in re.split(r'\n\s*\n|\\para\{', prose(source)) if p.strip()]
    long_sentences, semicolon_paragraphs = [], []
    for index, paragraph in enumerate(paragraphs, 1):
        semicolons = paragraph.count(';')
        if semicolons > 1:
            semicolon_paragraphs.append({'paragraph': index, 'count': semicolons})
        for sentence in sentences(paragraph):
            words = re.findall(r"[^\W_]+(?:[-'’][^\W_]+)*", sentence, flags=re.U)
            if len(words) > 45:
                long_sentences.append({'paragraph': index, 'words': len(words), 'text': sentence})
    return {'file': Path(path).as_posix(), 'para': len(re.findall(r'\\para\s*\{', source)),
            'emph': len(re.findall(r'\\emph\s*\{', source)),
            'long_sentences': long_sentences, 'semicolon_paragraphs': semicolon_paragraphs}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='+', type=Path)
    parser.add_argument('--scope', choices=('contributor', 'paper'), default='contributor')
    parser.add_argument('--strict', action='store_true', help='exit 1 when a limit is exceeded')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    files = set()
    for path in args.paths:
        if not path.exists():
            parser.error('missing input: ' + str(path))
        files.update(path.rglob('*.tex') if path.is_dir() else [path])
    if not files:
        parser.error('no TeX files found')
    reports = [count_file(path) for path in sorted(files)]
    totals = {'para': sum(r['para'] for r in reports), 'emph': sum(r['emph'] for r in reports),
              'long_sentences': sum(len(r['long_sentences']) for r in reports),
              'semicolon_paragraphs': sum(len(r['semicolon_paragraphs']) for r in reports)}
    limits = {'para': 15 if args.scope == 'paper' else 5,
              'emph': 30 if args.scope == 'paper' else 10,
              'long_sentences': 0, 'semicolon_paragraphs': 0}
    passed = all(totals[k] <= limits[k] for k in totals)
    if args.json:
        print(json.dumps({'files': reports, 'totals': totals, 'limits': limits, 'pass': passed},
                         ensure_ascii=False, indent=2))
    else:
        print('file\tpara\temph\tlong sentences\tparagraphs with >1 semicolon')
        for row in reports:
            print(f"{row['file']}\t{row['para']}\t{row['emph']}\t"
                  f"{len(row['long_sentences'])}\t{len(row['semicolon_paragraphs'])}")
            for issue in row['long_sentences']:
                print(f"  paragraph {issue['paragraph']}: {issue['words']} words: {issue['text']}")
        print('TOTAL ' + json.dumps(totals) + '; limits ' + json.dumps(limits))
        print('readability check: ' + ('PASS' if passed else 'FAIL') + ' (source estimate)')
    return 1 if args.strict and not passed else 0


if __name__ == '__main__':
    sys.exit(main())
