"""Clean GitBook-specific markup so MkDocs Material renders it correctly."""
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")

with open(os.path.join(os.environ["TEMP"], "gb_content.json"), encoding="utf-8") as f:
    content = json.load(f)

url_map = {}
for fobj in content["files"]:
    ext = os.path.splitext(fobj["name"])[1] or ".bin"
    url_map[fobj["downloadURL"]] = f"assets/{fobj['id']}{ext}"

HINT_STYLE = {"info": "info", "warning": "warning", "danger": "danger", "success": "success"}


def convert_hints(md):
    out, i, lines = [], 0, md.splitlines()
    while i < len(lines):
        m = re.match(r"\{%\s*hint\s+style=\"(\w+)\"\s*%\}", lines[i].strip())
        if m:
            style = HINT_STYLE.get(m.group(1), "note")
            body = []
            i += 1
            while i < len(lines) and "{% endhint %}" not in lines[i]:
                body.append(lines[i])
                i += 1
            i += 1  # skip endhint
            out.append(f'!!! {style} ""')
            for b in body:
                out.append("    " + b if b.strip() else "")
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out) + "\n"


for dirpath, _, files in os.walk(DOCS):
    for name in files:
        if not name.endswith(".md"):
            continue
        path = os.path.join(dirpath, name)
        with open(path, encoding="utf-8") as f:
            md = f.read()

        rel = os.path.relpath(path, DOCS).replace("\\", "/")
        prefix = "../" * rel.count("/")

        # normalize HTML-escaped ampersands inside gitbook file URLs, then localize
        md = re.sub(r"(https://\d+-files\.gitbook\.io/[^\"'\s)]+)",
                    lambda m: m.group(1).replace("&#x26;", "&"), md)
        for remote, local in url_map.items():
            md = md.replace(remote, prefix + local)

        # strip gitbook <mark> color spans
        md = re.sub(r'<mark style="[^"]*">', "", md)
        md = md.replace("</mark>", "")

        # gitbook hard line breaks: trailing backslash -> <br>
        md = re.sub(r"\\$", "<br>", md, flags=re.MULTILINE)

        md = convert_hints(md)

        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
        print("processed", rel)

# verify nothing remote is left
leftover = []
for dirpath, _, files in os.walk(DOCS):
    for name in files:
        if name.endswith(".md"):
            with open(os.path.join(dirpath, name), encoding="utf-8") as f:
                if "files.gitbook.io" in f.read():
                    leftover.append(name)
print("leftover remote urls:", leftover or "none")
