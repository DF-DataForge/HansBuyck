{
    "name": "Hans Buyck – Uitvoering inplannen (Enterprise)",
    "summary": "Bevestigde offerte maakt een in te plannen shift in Planning; inplannen zet de uitvoeringstaak op 'Ingepland'",
    "description": """
Enterprise-uitbreiding op *hansbuyck_workflow*:

* De dienst "Plaatsing ramen en deuren" wordt verkocht **per dag** en staat op
  *Diensten plannen* met de rol **Plaatser**: bij bevestiging van de offerte
  maakt Odoo (Sales Planning) een **in te plannen shift** aan.
* Offertes zonder die dienst krijgen als vangnet ook een shift (1 dag).
* Zodra de shift een plaatser + datum krijgt in **Planning**, of de taak een
  startdatum krijgt in de **Gantt**-weergave van het project, gaat de taak
  "Uitvoering van de werken" naar **Ingepland** (met datum en plaatser).
""",
    "version": "20.0.1.0.0",
    "category": "Services/Planning",
    "author": "Data Forge",
    "license": "OEEL-1",
    "depends": ["hansbuyck_workflow", "sale_planning", "project_enterprise"],
    "data": [
        "data/planning_data.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
}
