# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
общайся только на русском языке, несмотря на английский язык в этом файле!!

## Project overview

Django site for ESTIVO — a handmade premium woven-furniture brand (rope/rattan/veneer/HPL), migrated
from a Tilda site (estivo63.ru) to a custom Django build. Single `shop` app, no cart/checkout — the
business model is lead-generation: a visitor submits a request (product order or a consultation/B2B
lead), a manager follows up manually, and Telegram gets a best-effort notification. Orders and leads
are always persisted to Postgres first; Telegram delivery is never allowed to block or lose data.

## Setup and commands

Project root for Django commands is `internetshop/` (the inner directory containing `manage.py`), not the repo root.

```bash
cd internetshop
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r ../requirements.txt
python manage.py migrate
python manage.py seed_demo        # demo Material/Category/Collection/Product/Review data
python manage.py createsuperuser
python manage.py collectstatic    # required once — ManifestStaticFilesStorage fails template
                                   # rendering (missing manifest entry) if static isn't collected
python manage.py runserver
```

- Run all tests: `python manage.py test` (from `internetshop/`)
- Run a single test: `python manage.py test shop.tests.SmokeTests.<test_method>`
- No linter/formatter is configured in this repo.
- Static changes (CSS/JS/fonts) need `python manage.py collectstatic --noinput` before they show up
  correctly under `CompressedManifestStaticFilesStorage` — templates reference the manifest, not raw files.
- `CompressedManifestStaticFilesStorage` **fails collectstatic hard** if a CSS `url()` points at a
  missing file (e.g. a font). `shop/static/fonts/gilroy/` ships empty placeholder `.woff2` files for
  exactly this reason — don't delete them until real font files replace them.

### Required environment (`.env` in `internetshop/`, never committed)

- `BOT_TOKEN` — Telegram bot token from @BotFather
- `CHAT_ID` — Telegram chat/user id that receives order/lead notifications (the recipient must have
  sent `/start` to the bot first, or the Telegram API returns "chat not found")
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` — PostgreSQL connection
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` — standard Django settings, read via `os.environ` with dev-friendly defaults
- `SITE_URL` — public domain, used for sitemap/canonical/OG absolute URLs (defaults to `https://estivo63.ru`)

The project uses PostgreSQL (`psycopg2-binary`), not SQLite, despite a stray `db.sqlite3` in the tree.
`settings.py` forces `PGCLIENTENCODING=UTF8` before connecting — Windows locales (e.g. `Russian_Russia.1251`)
otherwise cause `UnicodeDecodeError` in psycopg2. `LANGUAGE_CODE='ru'`, `TIME_ZONE='Europe/Samara'`.

## Architecture

- `internetshop/internetshop/` — Django project config (`settings.py`, `urls.py`, `wsgi.py`/`asgi.py`).
  `urls.py` wires `handler404`, `sitemap.xml` (`shop/sitemaps.py`), and `robots.txt`.
- `internetshop/shop/` — the only app, flat structure (no sub-apps, no DRF). Models, views, forms,
  templates, and static assets all live here.

### Data model (`shop/models.py`)

`Material` (роуп/ротанг/шпон/HPL) and `Category` (кресла/диваны/…) are independent lookup tables —
a `Category` is not tied to one `Material` (tables come in HPL, veneer, etc.), so `Product` carries
both FKs separately. `Collection` groups products for homepage/showcase curation (`is_featured`).

`Product` uses a `slug` (auto-generated via `shop.utils.ru_slugify`, **not** Django's stock `slugify`
with `allow_unicode` — URLs must stay ASCII like the old Tilda site's `/kreslo`, `/divan`) and
`main_image`/`ProductImage` gallery (`ImageField`, not the old `image_url` string). Price fields:
`price` ("от"), `old_price` (for sales), plus spec fields (`max_load_kg`, `warranty_years`,
`temp_min_c`/`temp_max_c`) used directly in templates — no separate "specs" model.

`Order` and `Lead` are the two write paths from the public site:
- `Order` — a request tied to one `Product` (via `order_create`/`order_form.html`). `total_price` is
  snapshotted from `product.price` at save time so historical orders don't drift if prices change later.
- `Lead` — the shared model behind every other contact form (`lead_type`: private/designer/b2b),
  used by the B2B page, designer page, and general contact page via the shared `_lead_page()` view helper.

Both have a `telegram_notified` flag that is only set `True` when the Telegram send actually succeeds
(`shop.utils.notify_telegram` returns a bool, never raises) — the DB write always happens regardless
of Telegram outcome, so a bad token/blocked chat never loses a submission.

`Review` requires `is_published=True` to surface anywhere; nothing filters/moderates them automatically.

### Request flow (`shop/views.py` + `shop/urls.py`)

Catalog browsing nests by material then category: `catalog_list` → `catalog_by_material` →
`catalog_by_category`, all rendering the same `catalog_list.html` with different queryset filters and
`meta_title`/`meta_description` context (SEO copy follows the `"{Категория} из {материал}"` pattern
scraped from the original Tilda site). `product_detail` is slug-based.

Lead-capturing pages (`b2b_page`, `designers_page`, `contacts_page`) all funnel through
`_lead_page(request, template_name, lead_type)` — same POST/validate/save/notify logic, differing
only in template and default `lead_type`. `lead_create` is a separate POST-only endpoint for forms
embedded on pages that don't render their own `LeadForm` context (e.g. a hero CTA elsewhere).

`shop/context_processors.py` (`site_info`) injects brand contact info/socials/legal entity data into
every template's context — that's why `base.html`/`_header.html`/`_footer.html` reference
`site_info.*` without any view passing it explicitly.

### Templates and static

`base.html` + `partials/_header.html` / `_footer.html` / `_product_card.html` / `_lead_form.html` /
`_cta_section.html` / `_breadcrumbs.html` are the shared building blocks; page templates extend
`base.html` and override `meta_title`/`meta_description`/`og_*` blocks (defaults match the real
ESTIVO SEO copy carried over from Tilda).

CSS is hand-written vanilla, split by concern under `shop/static/css/`: `variables.css` (design
tokens — colors, spacing, the two-weight Gilroy setup), `base.css`, `layout.css` (header/footer/grid),
`components.css` (buttons/cards/forms/accordion), `pages.css` (page-specific sections). No
Bootstrap/Tailwind. `shop/static/js/` is small vanilla JS (mobile nav, scroll-reveal, phone mask,
product gallery) — no bundler, no framework.

Typography: headings use **Cormorant Garamond** (Google Fonts). Body/UI text uses **Gilroy**, which
is a paid font — only the Light (300) and ExtraBold (800) weights are freely licensed, so every
body-font `font-weight` in the CSS uses the `--weight-body-regular`/`--weight-body-bold` variables
instead of arbitrary values (no 400/500/600/700 body text exists on purpose). Real `.woff2` files go
in `shop/static/fonts/gilroy/` (see the `README.txt` there); until supplied, `@font-face` silently
falls back to the system sans-serif in `--font-body`.

Product/collection images are placeholders (`shop/static/img/placeholders/*.svg`) until real photos
are uploaded through the admin — `main_image`/`cover_image` are `blank=True`, and templates always
check `{% if product.main_image %}` before falling back to the placeholder.

### Admin and demo data

`shop/admin.py` registers every model with `list_display`/`list_filter`/`search_fields` — this is the
intended day-to-day content tool for the site owner (uploading photos, adjusting prices, working
Order/Lead queues), not just a debug view. `shop/management/commands/seed_demo.py` seeds
Material/Category/Collection/Product/Review rows with placeholder content for local development;
safe to rerun (`get_or_create`).

### Payment

There is intentionally no online payment integration. `Order.payment_status` exists as a future
extension point (see the `# TODO` comment above it in `models.py`) but wiring a real provider
(YooKassa/etc.) requires the site owner's own merchant account — don't add SDKs or webhook views for
this speculatively.
