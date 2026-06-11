"""Download all pages of the Valoria GitBook space as Markdown + images."""
import json
import os
import re
import sys
import urllib.request

TOKEN = os.environ["GITBOOK_TOKEN"]
SPACE = "ngoutjNUlevKbucIhxUO"
API = "https://api.gitbook.com/v1"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")


def api_get(path):
    req = urllib.request.Request(API + path, headers={"Authorization": f"Bearer {TOKEN}"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8"))


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r, open(dest, "wb") as f:
        f.write(r.read())


def walk(pages, acc):
    for p in pages:
        if p.get("type") == "document":
            acc.append(p)
        if p.get("pages"):
            walk(p["pages"], acc)


content = api_get(f"/spaces/{SPACE}/content")
docs = []
walk(content["pages"], docs)
print(f"{len(docs)} document pages")

# files: id -> (downloadURL, name)
os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
url_map = {}  # remote URL -> local relative path (from docs root)
for i, f in enumerate(content.get("files", [])):
    ext = os.path.splitext(f["name"])[1] or ".bin"
    local = f"assets/{f['id']}{ext}"
    dest = os.path.join(OUT, local)
    if not os.path.exists(dest):
        try:
            download(f["downloadURL"], dest)
            print(f"asset {i+1}: {local} ({f['size']} bytes)")
        except Exception as e:
            print(f"asset {i+1} FAILED: {e}", file=sys.stderr)
            continue
    url_map[f["downloadURL"]] = local

nav = []  # (path, title)
for p in docs:
    data = api_get(f"/spaces/{SPACE}/content/page/{p['id']}?format=markdown")
    md = data.get("markdown", "")
    path = p["path"]  # e.g. informaciya/fishki-servera/chat
    md_rel = "index.md" if path == "glavnaya" else f"{path}.md"
    dest = os.path.join(OUT, md_rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    depth = md_rel.count("/")
    prefix = "../" * depth

    # rewrite known asset URLs to local copies
    for remote, local in url_map.items():
        md = md.replace(remote, prefix + local)
    # also catch any gitbook file URL pattern left over (escaped variants)
    md = re.sub(r"https://\d+-files\.gitbook\.io/\S+?alt=media&token=[0-9a-f-]+", lambda m: m.group(0), md)

    if not md.lstrip().startswith("#"):
        md = f"# {p['title']}\n\n" + md
    with open(dest, "w", encoding="utf-8") as f:
        f.write(md)
    nav.append({"path": md_rel, "title": p["title"], "page_path": path})
    print(f"page: {md_rel} <- {p['title']}")

with open(os.path.join(os.path.dirname(OUT), "pages.json"), "w", encoding="utf-8") as f:
    json.dump(nav, f, ensure_ascii=False, indent=2)
print("done")
