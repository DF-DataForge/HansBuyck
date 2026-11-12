{
    "name": "Hans Buyck – Werkstroom website → CRM → project",
    "summary": "Contactformulier maakt een opportuniteit; bevestigde offerte maakt een project met een in te plannen uitvoeringstaak",
    "description": """
Werkstroom voor Hans Buyck BVBA:

1. Het contactformulier op de website maakt een **opportuniteit** aan in de
   CRM-pipeline van het verkoopteam "Website" (geen tussenstap via leads).
2. Vanuit de opportuniteit maakt u een offerte (standaard Odoo).
3. Bij **bevestiging** van de offerte wordt automatisch een **project**
   aangemaakt op basis van het sjabloon "Uitvoering ramen en deuren",
   met de taak **"Uitvoering van de werken"** in de fase *Te plannen* en een
   to-do "Uitvoering inplannen" voor de projectverantwoordelijke.

Dit gebeurt via de dienst "Plaatsing ramen en deuren" (standaard Odoo-mechanisme),
en als vangnet ook voor offertes zonder die dienst.
""",
    "version": "20.0.1.0.0",
    "category": "Sales/Sales",
    "author": "Data Forge",
    "license": "LGPL-3",
    "depends": ["website_crm", "sale_crm", "sale_project"],
    "data": [
        "data/crm_data.xml",
        "data/project_data.xml",
        "data/product_data.xml",
    ],
    "installable": True,
    "application": False,
}
