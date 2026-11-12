import logging

from markupsafe import Markup

_logger = logging.getLogger(__name__)

IMG = "/website_hansbuyck/static/src/img/"

PRODUCT_MENU = [
    ("Ramen", "/producten/ramen", "prod_ramen_cover.webp", "PVC, alu, hout, alu/hout"),
    ("Deuren", "/producten/deuren", "prod_deuren_cover.webp", "Veilig en isolerend"),
    ("Tuinkamers", "/producten/tuinkamers", "prod_tuinkamers_cover.webp", "Vrijstaand in de tuin"),
    ("Lichtstraten", "/producten/lichtstraten", "prod_lichtstraten_cover.webp", "In alle RAL-kleuren"),
    ("Veranda's", "/producten/verandas", "prod_verandas_cover.webp", "Extra leefruimte"),
    ("Glaswerken", "/producten/glaswerken", "prod_glaswerken_cover.webp", "Veiligheids-, isolerend en zonnewerend glas"),
]

MAIN_MENU = [
    ("Home", "/"),
    ("Producten", "/producten"),
    ("Beurzen", "/beurzen"),
    ("Folders", "/folders"),
    ("Vragen", "/vragen"),
    ("Contact", "/contact"),
]


def _mega_menu_html():
    items = "".join(
        f"""
            <div class="col-md-6 col-lg-4">
                <a href="{url}" class="hb_mega_item">
                    <img src="{IMG}{image}" alt="{name}" loading="lazy"/>
                    <span><strong>{name}</strong><small>{sub}</small></span>
                </a>
            </div>"""
        for name, url, image, sub in PRODUCT_MENU
    )
    return Markup(f"""
<section class="s_mega_menu_thumbnails hb_mega pt24 pb24 o_cc o_cc1" data-name="Mega menu producten">
    <div class="container">
        <div class="row g-2">{items}
        </div>
        <div class="d-flex justify-content-between align-items-center border-top mt-3 pt-3">
            <span class="text-muted small">Buitenschrijnwerk van de beste kwaliteit, geplaatst door ons eigen team.</span>
            <a href="/producten" class="btn btn-primary btn-sm">Alle producten</a>
        </div>
    </div>
</section>""")


def _setup_menu(env, website):
    """Replace the default top menu of the website with the Hans Buyck menu."""
    Menu = env["website.menu"].with_context(lang=website.default_lang_id.code or "en_US")
    root = website.menu_id
    root.child_id.unlink()
    for seq, (name, url) in enumerate(MAIN_MENU, start=1):
        vals = {
            "name": name,
            "url": url,
            "parent_id": root.id,
            "website_id": website.id,
            "sequence": seq * 10,
        }
        page = env["website.page"].search([("url", "=", url)], limit=1)
        if page and url != "/":
            vals["page_id"] = page.id
        if name == "Producten":
            vals["mega_menu_content"] = _mega_menu_html()
            vals["mega_menu_classes"] = "o_mega_menu_container_size"
        Menu.create(vals)


def _setup_language(env, website):
    """Dutch (Belgium) as the only website language."""
    lang_code = "nl_BE"
    lang = env["res.lang"]._activate_lang(lang_code)
    if not lang:
        _logger.warning("Language %s could not be activated", lang_code)
        return
    installed = env["ir.module.module"].search([("state", "=", "installed")]).mapped("name")
    try:
        env["ir.module.module"]._load_module_terms(installed, [lang_code])
    except Exception:  # translations are a nice-to-have, never block install
        _logger.exception("Could not load %s translations", lang_code)
    website.write({
        "language_ids": [(6, 0, lang.ids)],
        "default_lang_id": lang.id,
    })


def _disable_default_pages(env):
    """Unpublish Odoo demo pages replaced by our own (redirects are in data)."""
    for xmlid in ("website.contactus_page", "website.aboutus_page", "website.privacy_policy_page"):
        page = env.ref(xmlid, raise_if_not_found=False)
        if page:
            page.is_published = False


def post_init_hook(env):
    website = env.ref("base.default_website")
    _setup_language(env, website)
    _setup_menu(env, website)
    _disable_default_pages(env)
