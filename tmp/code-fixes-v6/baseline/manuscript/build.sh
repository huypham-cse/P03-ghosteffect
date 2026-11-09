#!/bin/sh
# pdflatex -> bibtex -> pdflatex x2 ; regenerate tables/figures/macros first
set -e
cd "$(dirname "$0")"
python3 ../artifact/scripts/render.py >/dev/null
pdflatex -interaction=nonstopmode main.tex >/dev/null 2>&1 || true
bibtex main >/dev/null 2>&1 || true
pdflatex -interaction=nonstopmode main.tex >/dev/null 2>&1 || true
pdflatex -interaction=nonstopmode main.tex >/dev/null 2>&1 || true
echo "errors: $(grep -ac '^!' main.log)"; echo "undefined: $(grep -aci 'undefined' main.log)"
grep -a "Overfull" main.log || true
grep -a "Output written" main.log
