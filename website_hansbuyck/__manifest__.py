{
    "name": "Hans Buyck – Website",
    "summary": "Website van Hans Buyck BVBA, ramen en deuren in Kortrijk (migratie van hansbuyck.be)",
    "description": """
Volledige website voor Hans Buyck BVBA, gemigreerd van hansbuyck.be naar Odoo 20.

* Huisstijl (kleuren, lettertypes, header, footer) als Odoo-themapalet
* Home, Producten (+6 productpagina's met fotogalerij), Beurzen (+4 detailpagina's),
  Folders (PDF-downloads), Vragen (FAQ), Contact (formulier -> CRM-lead), juridische pagina's
* Menu met mega-menu voor producten
* 301-redirects van de oude URL's (SEO-behoud)
* Alles bewerkbaar met de Odoo website builder
""",
    "version": "20.0.1.0.0",
    "category": "Website/Website",
    "author": "Data Forge",
    "license": "LGPL-3",
    "depends": ["website", "website_crm"],
    "data": [
        "data/company_data.xml",
        "views/layout.xml",
        "views/snippets.xml",
        "views/page_home.xml",
        "views/pages_producten.xml",
        "views/pages_beurzen.xml",
        "views/page_folders.xml",
        "views/page_vragen.xml",
        "views/page_contact.xml",
        "views/pages_legal.xml",
        "data/website_data.xml",
        "data/website_rewrite.xml",
    ],
    "assets": {
        "web._assets_primary_variables": [
            (
                "after",
                "website/static/src/scss/primary_variables.scss",
                "website_hansbuyck/static/src/scss/primary_variables.scss",
            ),
        ],
        "web.assets_frontend": [
            "website_hansbuyck/static/src/scss/hansbuyck.scss",
            "website_hansbuyck/static/src/interactions/*.js",
        ],
    },
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
}
