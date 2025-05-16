pandoc architecture.md \
  --filter pandoc-plantuml \
  --resource-path=.:plantuml-images \
  --pdf-engine=xelatex \
  -o architecture.pdf

