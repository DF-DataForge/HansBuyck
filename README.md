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

## Workflow: website → CRM → project (`hansbuyck_workflow`)

A second module, [`hansbuyck_workflow`](hansbuyck_workflow/), adds the sales-to-execution flow:

1. **Contact form → opportunity.** Every submission of the website contact form creates an **opportunity** in the *Website* sales team's pipeline. There is no leads step: the team has *Leads* switched off and is the website's default CRM team. Name, e-mail, phone, subject and question go into the matching fields. Address, postcode, municipality, interest and privacy consent go into the description.
2. **Opportunity → quotation.** Use Odoo's standard *New Quotation* button on the opportunity.
3. **Confirmed quotation → opportunity won.** Confirming the quotation marks its opportunity as **won** (won stage, 100 % probability, with a note in the chatter). An opportunity that was marked lost is re-opened and set to won as well.
4. **Confirmed quotation → project with execution task.** On confirmation, Odoo creates a project from the template **"Uitvoering ramen en deuren"**:
   - Stages: *Te plannen → Ingepland → In uitvoering → Opgeleverd*.
   - It contains the task **"Uitvoering van de werken"**, linked to the customer and the sales order, with a checklist. The task starts in *Te plannen*.
   - The project manager (the quote's salesperson if the template has none) gets a to-do **"Uitvoering inplannen"**, due in 2 days.
   - Add the service **"Plaatsing ramen en deuren"** to the quote: standard Odoo then creates the project and links the task to that order line. A safety net creates the same project for quotations without that service, so **every** confirmed quotation gets one.
   - Re-confirming an order does not create a second project.

**Planning the task:** see the Enterprise module below. Without it (Community), set assignees, a deadline and allocated hours, move the task to *Ingepland*, and use the project's *Calendar* view.

## Enterprise: planning the execution (`hansbuyck_workflow_planning`)

A third module, [`hansbuyck_workflow_planning`](hansbuyck_workflow_planning/), connects the execution to the **Planning** app and the project **Gantt** view. It needs Odoo Enterprise (`sale_planning`, `project_enterprise`).

- **The service is sold per day.** "Plaatsing ramen en deuren" is set to unit *Days*, *Plan Services* on, role **Plaatser**. When the quotation is confirmed, Sales Planning creates a **shift to plan** for that number of days (1 day = 8 h).
- **Safety net:** a confirmed quotation without that service still gets one shift of 1 day for the Plaatser role.
- **Planning in the Planning app:** when a shift gets a fitter and a date, the task "Uitvoering van de werken" moves to *Ingepland*. It gets the same start and end dates, and the fitter is added as an assignee.
- **Planning in the Gantt view:** giving the task a start date in the project's Gantt view also moves it to *Ingepland*.
- **Linking shifts to the project:** if Planning's project integration is installed (so shifts have a *Project* field), the shift is linked to the order's project.

> ⚠️ **Written without access to the Enterprise source code.** The Enterprise fields it uses were written from knowledge of earlier versions:
> - `product.template.planning_enabled` and `planning_role_id`,
> - `planning.slot.sale_line_id`, `resource_id`, `start_datetime`, `end_datetime`, `allocated_hours`, `role_id`, `project_id`,
> - `project.task.planned_date_begin`.
>
> The code checks that each field exists before using it, so a renamed field logs a warning instead of breaking the install. **Run the tests on staging** (see below) and check the install log for `hansbuyck_workflow_planning:` warnings.

## Installation

Requirements:

- Odoo **20.0** with the `website` and `website_crm` apps.
- For `hansbuyck_workflow_planning`: **Odoo Enterprise** with Planning and Project.
- Custom modules need **Odoo.sh, Cloudpepper or on-premise**. Odoo Online cannot install them.

### Cloudpepper

1. In Cloudpepper, open the server, then *Git repositories* (custom addons), and add this repository with branch `claude/adoring-euler-3385gy`, or the branch you merge it into. For a private repository, add Cloudpepper's deploy key to GitHub first.
2. Attach the repository to the **staging** instance and deploy/pull. Cloudpepper adds it to the addons path.
3. In Odoo: *Apps → Update Apps List*, then install in this order:
   - **Hans Buyck – Website** (`website_hansbuyck`)
   - **Hans Buyck – Werkstroom website → CRM → project** (`hansbuyck_workflow`)
   - **Hans Buyck – Uitvoering inplannen (Enterprise)** (`hansbuyck_workflow_planning`)
4. For later updates: pull in Cloudpepper, then *Upgrade* the modules in Apps, or restart with `-u <module>`.

### Command line (on-premise, or Cloudpepper's shell)
Everything is ordinary configuration (sales team, project template, stages, product) and can be changed in Odoo without code.

## Installation

Requirements:

- Odoo **20.0** with the `website` and `website_crm` apps.
- Custom modules need **Odoo.sh or on-premise**. Odoo Online cannot install them.

```bash
odoo -d <database> -i website_hansbuyck,hansbuyck_workflow,hansbuyck_workflow_planning
```

The website module's install hook does three things:

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

## Tests

Run these on the **staging** database. They create test records but roll everything back.

```bash
odoo -d <staging-db> -u hansbuyck_workflow,hansbuyck_workflow_planning --test-tags /hansbuyck_workflow:TestHansBuyckWorkflow,/hansbuyck_workflow:TestHansBuyckWebsiteForm,/hansbuyck_workflow_planning:TestHansBuyckPlanning --stop-after-init
```

The Enterprise tests (`TestHansBuyckPlanning`) check:
- the product is set to days, planning on, role Plaatser,
- a confirmed quotation with 2 days of installation gives a 16 h shift,
- the safety-net shift for quotations without the service,
- assigning a fitter and date to the shift moves the task to *Ingepland* with dates and assignee,
- Gantt planning moves the task too.

So far these only ran against stand-ins for the Enterprise modules, which proves the code runs but not that the field names match real Enterprise.

The 9 workflow tests (Community) check:
- website form → opportunity in the Website team,
- confirmation marks the opportunity won (also when it was lost), and a quotation alone does not,
- confirming with and without the installation service creates exactly one project with the execution task, the stages and the to-do,
- re-confirming creates no duplicate,
- drafts get no project,
- the template stays unchanged.

## Development

- Module structure: `views/` (pages and layout), `data/` (company, website, redirects), `static/src/scss` (palette and components), `static/src/interactions` (gallery lightbox), `static/src/img` (optimised WebP images), `static/pdf` (brochures).
- Tested on Odoo 20.0 (nightly 2026-11-12) on Python 3.13:
  - clean install and module update,
  - all pages return 200 and every redirect returns 301,
  - no JS or SCSS errors,
  - contact form → CRM lead,
  - mega menu, lightbox, and the editor opening on the pages.
