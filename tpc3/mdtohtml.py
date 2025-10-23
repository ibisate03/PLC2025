#!/usr/bin/env python3
import sys
import re
from pathlib import Path


# #, ##, ### headers; **bold**; *italic*; ordered list items "1. ...";
# links [text](url); images ![alt](url)

IMG = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
BOLD = re.compile(r'\*\*(.+?)\*\*')
ITAL = re.compile(r'(?<!\*)\*(.+?)\*(?!\*)')
HEAD = re.compile(r'^(#{1,3})\s+(.*)$')
OLI  = re.compile(r'^\s*\d+\.\s+(.*)$')

def inline_md(s: str) -> str:
    s = IMG.sub(r'<img alt="\1" src="\2" />', s)
    s = LINK.sub(r'<a href="\2">\1</a>', s)
    s = BOLD.sub(r'<strong>\1</strong>', s)
    s = ITAL.sub(r'<em>\1</em>', s)
    return s

def md_to_html(lines):
    out = []
    in_ol = False

    def close_ol():
        nonlocal in_ol
        if in_ol:
            out.append('</ol>')
            in_ol = False

    for raw in lines:
        line = raw.rstrip('\n')

        if not line.strip():
            close_ol()
            out.append('')
            continue

        m = HEAD.match(line)
        if m:
            close_ol()
            level = len(m.group(1))
            out.append(f'<h{level}>' + inline_md(m.group(2).strip()) + f'</h{level}>')
            continue

        m = OLI.match(line)
        if m:
            if not in_ol:
                out.append('<ol>')
                in_ol = True
            out.append('  <li>' + inline_md(m.group(1).strip()) + '</li>')
            continue
        else:
            close_ol()

        out.append('<p>' + inline_md(line.strip()) + '</p>')

    close_ol()
    return '\n'.join(out)

def convert(inp: Path, outp: Path|None):
    body = md_to_html(inp.read_text(encoding='utf-8').splitlines(True))
    html = (
        "<!doctype html>\n<html>\n<head>\n<meta charset=\"utf-8\">\n"
        "<title>Converted</title>\n</head>\n<body>\n"
        + body +
        "\n</body>\n</html>\n"
    )
    if outp is None:
        sys.stdout.write(html)
    else:
        outp.write_text(html, encoding='utf-8')

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python md2html.py <input.md> [output.html]")
        sys.exit(1)
    inp = Path(sys.argv[1])
    if not inp.exists():
        print("Input file not found", file=sys.stderr)
        sys.exit(2)
    outp = Path(sys.argv[2]) if len(sys.argv) == 3 else None
    convert(inp, outp)

if __name__ == "__main__":
    main()
