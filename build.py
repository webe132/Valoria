"""Build the Valoria static site: docs/*.md + web/ templates -> site/."""
import html
import json
import os
import re
import shutil

import markdown
from jinja2 import Environment, FileSystemLoader

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")
WEB = os.path.join(ROOT, "web")
OUT = os.path.join(ROOT, "site")

NAV = [
    {
        "group": "Информация",
        "items": [
            {"title": "Команды", "icon": "⌨️", "path": "informaciya/komandy"},
            {
                "title": "Фишки сервера",
                "icon": "✨",
                "path": "informaciya/fishki-servera",
                "children": [
                    {"title": "Технологии", "icon": "⚙️", "path": "informaciya/fishki-servera/tekhnologii"},
                    {"title": "Кастомные крафты", "icon": "🛠️", "path": "informaciya/fishki-servera/kastomnye-krafty"},
                    {"title": "Быстрое опадение листвы", "icon": "🍃", "path": "informaciya/fishki-servera/bystroe-opadenie-listvy"},
                    {"title": "Быстрый бетон", "icon": "🧱", "path": "informaciya/fishki-servera/bystryi-beton"},
                    {"title": "Чат", "icon": "💬", "path": "informaciya/fishki-servera/chat"},
                    {"title": "Мини-блоки", "icon": "🧊", "path": "informaciya/fishki-servera/mini-bloki"},
                    {"title": "Некопируемые арты и шаблоны", "icon": "🖼️", "path": "informaciya/fishki-servera/nekopiruemye-arty-i-shablony"},
                    {"title": "Невидимые рамки", "icon": "🔲", "path": "informaciya/fishki-servera/nevidimye-ramki"},
                    {"title": "PlasmoVoice и EmoteCraft", "icon": "🎙️", "path": "informaciya/fishki-servera/plasmovoice-i-emotecraft"},
                    {"title": "Пластинки", "icon": "💿", "path": "informaciya/fishki-servera/plastinki"},
                    {"title": "Портал любой формы", "icon": "🌀", "path": "informaciya/fishki-servera/portal-lyuboi-formy"},
                    {"title": "Редактирование стоек для брони", "icon": "🛡️", "path": "informaciya/fishki-servera/redaktirovanie-stoek-dlya-broni"},
                    {"title": "Скрытые никнеймы", "icon": "🕶️", "path": "informaciya/fishki-servera/skrytye-nikneimy"},
                    {"title": "Выпадение голов", "icon": "💀", "path": "informaciya/fishki-servera/vypadenie-golov"},
                    {"title": "Ограничение элитр", "icon": "✈️", "path": "informaciya/fishki-servera/ogranichenie-elitr"},
                    {"title": "Командная защита", "icon": "🤝", "path": "informaciya/fishki-servera/komandnaya-zashita"},
                    {"title": "Улучшения для счастливых гастов", "icon": "👻", "path": "informaciya/fishki-servera/uluchsheniya-dlya-schastlivykh-gastov"},
                    {"title": "Алкоголизм", "icon": "🍺", "path": "informaciya/fishki-servera/alkogolizm"},
                    {"title": "Мелкие механики", "icon": "🚩", "path": "informaciya/fishki-servera/melkie-mekhaniki"},
                ],
            },
        ],
    },
    {
        "group": "Прочая информация",
        "items": [
            {"title": "Работать с нами", "icon": "💼", "path": "prochaya-informaciya/rabotat-s-nami"},
            {"title": "Спонсорство", "icon": "💖", "path": "prochaya-informaciya/sponsorstvo"},
        ],
    },
]


def flatten(nav):
    flat = []
    for group in nav:
        for item in group["items"]:
            flat.append(item)
            flat.extend(item.get("children", []))
    return flat


def md_to_html(md_text, depth):
    # strip leading "# Title" - the template renders the page header itself
    md_text = re.sub(r"^#\s+.*\n", "", md_text.lstrip(), count=1)
    # rewrite asset references for the new output depth (pages live one level deeper)
    md_text = re.sub(r"(\.\./)*assets/", "../" * depth + "assets/", md_text)
    # drop GitBook hidden table columns (always trailing empty cells)
    md_text = md_text.replace("<th data-hidden></th>", "").replace("<td></td></tr>", "</tr>")
    return markdown.markdown(
        md_text,
        extensions=["admonition", "attr_list", "md_in_html", "tables"],
    )


def text_of(html_text):
    text = re.sub(r"<[^>]+>", " ", html_text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


env = Environment(loader=FileSystemLoader(os.path.join(WEB, "templates")), autoescape=False)

# clear site/ but keep its .git: the gh-pages branch is pushed from there
os.makedirs(OUT, exist_ok=True)
for entry in os.listdir(OUT):
    if entry == ".git":
        continue
    full = os.path.join(OUT, entry)
    shutil.rmtree(full) if os.path.isdir(full) else os.remove(full)
shutil.copytree(os.path.join(DOCS, "assets"), os.path.join(OUT, "assets"))
os.makedirs(os.path.join(OUT, "static"))
for f in ("style.css", "app.js"):
    shutil.copy(os.path.join(WEB, f), os.path.join(OUT, "static", f))
open(os.path.join(OUT, ".nojekyll"), "w").close()

pages = flatten(NAV)
search_index = []

# landing page
landing = env.get_template("landing.html")
with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
    f.write(landing.render(root="", nav=NAV, active=None, title="Valoria - приватный Minecraft-сервер"))

# wiki pages
wiki = env.get_template("wiki.html")
for i, page in enumerate(pages):
    depth = page["path"].count("/") + 1
    src = os.path.join(DOCS, page["path"].replace("/", os.sep) + ".md")
    with open(src, encoding="utf-8") as f:
        body = md_to_html(f.read(), depth)

    # the "Фишки сервера" overview is empty in GitBook - render a card grid instead
    cards = page.get("children") if not text_of(body) else None

    out_dir = os.path.join(OUT, page["path"].replace("/", os.sep))
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(wiki.render(
            root="../" * depth,
            nav=NAV,
            active=page["path"],
            page=page,
            body=body,
            cards=cards,
            prev=pages[i - 1] if i > 0 else None,
            next=pages[i + 1] if i + 1 < len(pages) else None,
            title=f"{page['title']} - Valoria Wiki",
        ))
    search_index.append({
        "title": page["title"],
        "icon": page["icon"],
        "url": page["path"] + "/",
        "text": text_of(body)[:4000],
    })

with open(os.path.join(OUT, "search-index.json"), "w", encoding="utf-8") as f:
    json.dump(search_index, f, ensure_ascii=False)

# 404 page
notfound = env.get_template("404.html")
with open(os.path.join(OUT, "404.html"), "w", encoding="utf-8") as f:
    f.write(notfound.render(root="", nav=NAV, active=None, title="404 - Valoria"))

print(f"built {len(pages)} wiki pages + landing -> {OUT}")
