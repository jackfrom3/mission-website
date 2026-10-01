# Mission Performance SB website

Static site, hosted on GitHub Pages.

- Edit content in `build.py`, then run `python3 build.py` to regenerate the HTML.
- Styles: `assets/site.css`. Photos: `img/`.
- Newsletter articles: `newsletter/articles.json` (imported once from Substack via `tools/import_substack.py`).
- `TESTING = True` in build.py keeps the site out of search engines; flip it when the real domain points here.
- Forms post to Web3Forms; set `WEB3FORMS_KEY` in build.py.
