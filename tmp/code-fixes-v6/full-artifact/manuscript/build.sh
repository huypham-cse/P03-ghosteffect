#!/bin/sh
# pdflatex -> bibtex -> pdflatex x2 ; regenerate tables/figures/macros first
set -eu
cd "$(dirname "$0")"
"${PYTHON:-python3}" ../artifact/scripts/render.py
pdflatex -halt-on-error -file-line-error -interaction=nonstopmode main.tex
bibtex main
pdflatex -halt-on-error -file-line-error -interaction=nonstopmode main.tex
pdflatex -halt-on-error -file-line-error -interaction=nonstopmode main.tex
test -s main.pdf
if grep -aE 'LaTeX Warning:.*undefined|There were undefined references|^!' main.log; then
  echo 'build failed: unresolved references/citations or LaTeX errors' >&2
  exit 1
fi
grep -a "Overfull" main.log || true
grep -a "Output written" main.log
