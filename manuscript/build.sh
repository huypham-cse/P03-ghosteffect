#!/bin/sh
# pdflatex -> bibtex -> pdflatex ; figures -> pdflatex. Regenerate tables/figures/macros first.
# The TikZ/pgfplots figures are prebuilt PDFs in figures/ext/ (see main.tex) so that Overleaf's free plan, which stops
# a compile after 10 s, only includes them. They are rebuilt here, one pdflatex job per picture, after the main passes
# have closed main.aux and main.out, so every cross-reference inside a picture is final (Figure 1 cites a theorem).
set -eu
cd "$(dirname "$0")"
"${PYTHON:-python3}" ../artifact/scripts/render.py
mkdir -p figures/ext
TEX="pdflatex -halt-on-error -file-line-error -interaction=nonstopmode"
$TEX main.tex
bibtex main
$TEX main.tex
if [ -s main.figlist ]; then
  rm -f figures/ext/*
  while read -r img; do
    $TEX -jobname "$img" "\def\tikzexternalrealjob{main}\input{main}" > /dev/null
    rm -f "$img.log" "$img.aux" "$img.out"
  done < main.figlist
fi
$TEX main.tex
test -s main.pdf
if grep -aE 'LaTeX Warning:.*undefined|There were undefined references|^!' main.log; then
  echo 'build failed: unresolved references/citations or LaTeX errors' >&2
  exit 1
fi
grep -a "Overfull" main.log || true
grep -a "Output written" main.log
