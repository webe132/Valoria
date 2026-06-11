# Valoria — сайт и вики

Сайт приватного Minecraft-сервера **Valoria**: лендинг + вики. Перенесён с GitBook (`wiki.valorian.fun`) на GitHub Pages.

## Как устроено

- `docs/` — контент вики в Markdown (страницы как в GitBook) и картинки в `docs/assets/`
- `web/` — дизайн: шаблоны (Jinja2), `style.css`, `app.js`
- `build.py` — генератор: собирает `docs/` + `web/` в статический сайт в `site/`
- `.github/workflows/deploy.yml` — автодеплой на GitHub Pages при пуше в `main`

## Как редактировать

Текст страниц — правь Markdown в `docs/`. Меню и порядок страниц — список `NAV` в начале `build.py`. Дизайн — `web/style.css` и шаблоны в `web/templates/`.

Локальный предпросмотр:

```
pip install markdown jinja2
python build.py
python -m http.server -d site 8000
```

`fetch_gitbook.py` и `postprocess.py` — одноразовые скрипты миграции с GitBook, для сайта не нужны.
