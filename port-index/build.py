"""Build the page from template.html.

Writes two files:
  index.html     standalone page for GitHub Pages
  artifact.html  fragment for the Claude artifact (the host adds its own <head>)
"""
from pathlib import Path

here = Path(__file__).parent
body = (here / "template.html").read_text()
body = body.replace("__WORLD__", (here / "data/world-110m.json").read_text())
body = body.replace("__US__", (here / "data/states-10m.json").read_text())

(here / "artifact.html").write_text(body)
(here / "index.html").write_text(
    '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    "<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n"
    + body
    + "\n</html>\n"
)
print("built index.html and artifact.html")
