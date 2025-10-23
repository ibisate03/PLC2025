#!/usr/bin/env python3
import sys
import re
from pathlib import Path

"""

Supported:
- Keywords: SELECT, WHERE, DISTINCT, LIMIT, OFFSET, FILTER, OPTIONAL
- Variables: ?name
- IRIs: <http://...>
- Prefixed names: prefix:local (e.g., foaf:name)
- Strings: "text" (no multiline)
- Numbers: 123 (integers)
- Booleans: true, false
- Punct: { } ( ) . , ; *
- Operators: =, !=, <, >, <=, >=
- Comments: lines starting with '#'
- Whitespace is ignored

Output: one token per line -> TYPE\tVALUE
"""

TOKEN_SPECS = [
    ("COMMENT",      r"\#.*?$"),
    ("WS",           r"[ \t\r\n]+"),
    ("KEYWORD",      r"\b(SELECT|WHERE|DISTINCT|LIMIT|OFFSET|FILTER|OPTIONAL)\b"),
    ("BOOLEAN",      r"\b(true|false)\b"),
    ("OP",           r"(<=|>=|!=|=|<|>)"),
    ("LBRACE",       r"\{"),
    ("RBRACE",       r"\}"),
    ("LPAREN",       r"\("),
    ("RPAREN",       r"\)"),
    ("DOT",          r"\."),
    ("COMMA",        r","),
    ("SEMI",         r";"),
    ("STAR",         r"\*"),
    ("IRI",          r"<[^<>\s]+>"),
    ("STRING",       r"\"([^\"\\]|\\.)*\""),
    ("VAR",          r"\?[A-Za-z_][A-Za-z0-9_]*"),
    ("NUMBER",       r"\b\d+\b"),
    ("PNAME",        r"[A-Za-z_][A-Za-z0-9_]*:[A-Za-z_][A-Za-z0-9_\-]*"),
    ("IDENT",        r"[A-Za-z_][A-Za-z0-9_]*"),
    ("MISMATCH",     r".")
]

MASTER_RE = re.compile(
    "|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPECS),
    re.MULTILINE
)

def tokenize(text: str):
    for m in MASTER_RE.finditer(text):
        kind = m.lastgroup
        value = m.group()
        if kind == "WS" or kind == "COMMENT":
            continue
        if kind == "KEYWORD":
            value = value.upper()
        if kind == "STRING":
            pass
        if kind == "PNAME":
            pass
        if kind == "MISMATCH":
            yield ("ERROR", value)
            continue
        yield (kind, value)

def lex_file(path: Path):
    src = path.read_text(encoding="utf-8")
    return list(tokenize(src))

def main():
    if len(sys.argv) != 2:
        print("Usage: python lexer.py <input.sparql>", file=sys.stderr)
        sys.exit(1)

    p = Path(sys.argv[1])
    if not p.exists():
        print(f"File not found: {p}", file=sys.stderr)
        sys.exit(2)

    toks = lex_file(p)
    for ttype, tval in toks:
        print(f"{ttype}\t{tval}")

if __name__ == "__main__":
    main()
