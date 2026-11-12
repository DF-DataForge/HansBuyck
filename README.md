# Hans Buyck – Odoo 20 website

This is a migration of [hansbuyck.be](https://www.hansbuyck.be) to an **Odoo 20** website. It keeps the same page structure and has a new, modern design.

The whole site is one installable module: [`website_hansbuyck`](website_hansbuyck/).

## What's inside

| Old site | New Odoo page | Notes |
|---|---|---|
| `/` Home | `/` | Hero slider (3 slides), selling points, welcome text, product grid, how-we-work steps, video and regions, scrolling ticker, Instagram, call-to-action |
| `/producten/` | `/producten` | 6 product cards and a "why Hans Buyck" section |
| 6 product pages | `/producten/ramen`, `/deuren`, `/tuinkamers`, `/lichtstraten`, `/verandas`, `/glaswerken` | Original text, a sticky advice box, related PDF brochures, a full photo gallery (masonry + lightbox), 130+ photos |
| `/beurzen/` + 4 fairs | `/beurzen`, `/beurzen/bis-gent`, `/bouwxpo-kortrijk`, `/bouwen-wonen-nu-brugge`, `/bouwbeurs-roeselare` | |
| `/folders/` | `/folders` | 13 PDF brochures, grouped by material (Alu / PVC / Hout / Hout-alu), with file sizes |
| `/vragen/` | `/vragen` | FAQ accordion (8 questions) |
| `/contact/` | `/contact` (+ `/contact-bedankt`) | The form creates a **CRM lead** (name, e-mail, phone, subject, question; address, postcode, municipality, interest and privacy consent go into the description). Also contact details, opening hours, route link and map |
| `/gdpr/...` | `/disclaimer`, `/privacyverklaring`, `/cookieverklaring` | Original legal text |

Other features:

- **Brand style as an Odoo theme palette**: brand yellow `#FEF013` and anthracite, Barlow / Barlow Condensed fonts. You can still change these under *Website → Theme* in the builder.
- **Header**: top bar (address, phone, e-mail, Facebook), sticky header, mega menu under *Producten*, and a "Vrijblijvende offerte" button.
- **Footer**: about text, contact details, opening hours, product links and legal links.
- **SEO**:
  - 32 **301 redirects** from the old URLs (product, fair and GDPR pages, `/uploads/*.pdf`), so existing links and Google rankings keep working.
  - Meta title and description on every page.
- **GDPR**: Odoo cookie bar linked to the cookie statement. YouTube is embedded through `youtube-nocookie`, and maps and video only load after cookie consent.
- **Language**: Dutch (nl_BE) is set as the website language.
- **Editable**: every section is a normal Odoo block, so text, images and buttons can be changed in the website builder.

## Installation

Requirements:

- Odoo **20.0** with the `website` and `website_crm` apps.
- Custom modules need **Odoo.sh or on-premise**. Odoo Online cannot install them.

Steps:

1. Add this repository to your addons path (on Odoo.sh: push it to the project's repository).
2. Install the module:

```bash
odoo -d <database> -i website_hansbuyck
```

The install hook does three things:

- replaces the default top menu with the Hans Buyck menu, including the mega menu,
- activates nl_BE as the website language,
- unpublishes Odoo's default `/contactus`, `/aboutus` and `/privacy` pages (they redirect to the new pages).

Install it on a fresh database, or on a database where the website has not been customised yet: the hook overwrites the current top menu. Company data (address, phone, e-mail, logo, social links) is set once (`noupdate`), so changes you make later in Odoo are kept.

## Points to check with the customer

- **VAT number**: the old site shows `BE0455.307.913`, but that number fails the Belgian checksum. Odoo refuses it, so it is only shown as text. Please confirm the correct number and enter it on the company.
- **Outdated content** (copied as-is from the old site):
  - the dates of the Roeselare fair (2024),
  - premium amounts that still mention Eandis/Infrax (now Fluvius).
- **Instagram**: the original 4 posts are linked. The Instagram profile name is not on the old site; add it to the company's social links if you want a "follow us" button.
- The external *proxi.tools* video player on the old homepage was not migrated. The YouTube video is.

## Development

- Module structure: `views/` (pages and layout), `data/` (company, website, redirects), `static/src/scss` (palette and components), `static/src/interactions` (gallery lightbox), `static/src/img` (optimised WebP images), `static/pdf` (brochures).
- Tested on Odoo 20.0 (nightly 2026-11-12) on Python 3.13:
  - clean install and module update,
  - all pages return 200 and every redirect returns 301,
  - no JS or SCSS errors,
  - contact form → CRM lead,
  - mega menu, lightbox, and the editor opening on the pages.
