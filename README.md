# Valoria Wiki

Вики приватного Minecraft-сервера **Valoria**. Перенесена с GitBook (`wiki.valorian.fun`) на GitHub Pages.

Сайт собирается [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) и автоматически деплоится GitHub Actions при каждом пуше в `main`.

## Как редактировать

Страницы — обычный Markdown в папке `docs/`. Меню сайта — секция `nav` в `mkdocs.yml`.

Локальный предпросмотр:

```
pip install mkdocs-material
mkdocs serve
```

`fetch_gitbook.py` и `postprocess.py` — одноразовые скрипты миграции с GitBook, для работы сайта не нужны.
