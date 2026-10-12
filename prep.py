#!/usr/bin/env python3
"""Turn a `git archive` snapshot of the Nazm repo (docs/ + README.md) into an mdBook src/ tree.

- docs/X.md          -> src/X.md
- README.md          -> src/README.md (the book's introduction)
- docs/grammar.ebnf  -> src/grammar.md (wrapped in a code fence)
- Links that resolve to another page inside docs/ are kept (made relative to the new location).
- Links that leave docs/ (crates/, tests/, ...) point into a private repository, so they are
  rendered as plain code text.
- ```nazm fences are highlighted as Rust (highlight.js has no Nazm grammar).
"""
import os
import posixpath
import re
import shutil
import sys

snap, src = sys.argv[1], sys.argv[2]
docs = os.path.join(snap, "docs")

LINK = re.compile(r"(!?)\[([^\]\n]*)\]\(([^)\s]+)\)")


def rewrite_link(m, origin_dir):
    bang, text, target = m.groups()
    if bang or re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
        return m.group(0)
    path, _, frag = target.partition("#")
    # origin_dir is the file's directory relative to the repo root, e.g. "docs/releases" or "".
    resolved = posixpath.normpath(posixpath.join(origin_dir, path))
    if not os.path.isfile(os.path.join(snap, resolved)):
        # Some pages write repo-root paths ("docs/roadmap.md") from inside docs/.
        resolved = posixpath.normpath(path)
    if resolved.startswith("docs/") and os.path.isfile(os.path.join(snap, resolved)):
        inner = resolved[len("docs/"):]
        if inner == "grammar.ebnf":
            inner = "grammar.md"
        here = origin_dir[len("docs/"):] if origin_dir.startswith("docs/") else ""
        rel = posixpath.relpath(inner, here or ".")
        return f"[{text}]({rel}{'#' + frag if frag else ''})"
    # Outside docs/: the repository is private, keep the name but drop the link.
    shown = text if text.startswith("`") else f"`{text}`" if text == target else text
    return shown


def rewrite_line(line, origin_dir):
    # Skip links that start inside an inline code span (link text may itself contain code).
    spans = [m.span() for m in re.finditer(r"(`+)[^`]*?\1", line)]

    def sub(m):
        if any(a <= m.start() < b for a, b in spans):
            return m.group(0)
        return rewrite_link(m, origin_dir)

    return LINK.sub(sub, line)


def convert(src_path, dst_path, origin_dir):
    out, fence = [], None
    with open(src_path, encoding="utf-8") as f:
        for line in f:
            stripped = line.lstrip()
            m = re.match(r"(`{3,}|~{3,})(\S*)", stripped)
            if fence is None and m:
                fence = m.group(1)
                if m.group(2) == "nazm":
                    line = line.replace(fence + "nazm", fence + "rust", 1)
            elif fence is not None and stripped.startswith(fence) and stripped.strip() == fence:
                fence = None
            elif fence is None:
                line = rewrite_line(line, origin_dir)
            out.append(line)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, "w", encoding="utf-8") as f:
        f.writelines(out)


shutil.rmtree(src, ignore_errors=True)
for root, _, files in os.walk(docs):
    for name in files:
        full = os.path.join(root, name)
        rel = os.path.relpath(full, docs)
        if name.endswith(".md"):
            convert(full, os.path.join(src, rel), posixpath.join("docs", os.path.dirname(rel)).rstrip("/"))

convert(os.path.join(snap, "README.md"), os.path.join(src, "README.md"), "")

with open(os.path.join(docs, "grammar.ebnf"), encoding="utf-8") as f:
    grammar = f.read()
with open(os.path.join(src, "grammar.md"), "w", encoding="utf-8") as f:
    f.write("# Grammar\n\nThe Nazm grammar in EBNF, as committed in `docs/grammar.ebnf`.\n\n```ebnf\n")
    f.write(grammar.rstrip("\n") + "\n```\n")
