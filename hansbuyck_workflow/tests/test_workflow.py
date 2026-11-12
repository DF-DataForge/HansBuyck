from odoo.tests import HttpCase, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHansBuyckWorkflow(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Klant Test", "email": "klant@example.com"})
        cls.goods = cls.env["product.product"].create({"name": "PVC raam 120x140", "type": "consu", "list_price": 650})
        cls.plaatsing = cls.env.ref("hansbuyck_workflow.product_plaatsing").product_variant_id
        cls.template = cls.env.ref("hansbuyck_workflow.project_template_uitvoering")

    def _order(self, products):
        return self.env["sale.order"].create({
            "partner_id": self.partner.id,
            "order_line": [(0, 0, {"product_id": p.id, "product_uom_qty": 1}) for p in products],
        })

    def _assert_execution_project(self, order):
        projects = order.project_id | order.order_line.project_id
        self.assertEqual(len(projects), 1, "exactly one project per confirmed quotation")
        self.assertFalse(projects.is_template)
        self.assertIn(order.name, projects.name)
        self.assertEqual(projects.partner_id, self.partner)
        self.assertEqual(order.project_id, projects, "project visible from the quotation")
        task = projects.tasks.filtered(lambda t: t.name == "Uitvoering van de werken")
        self.assertEqual(len(task), 1, "one execution task")
        self.assertEqual(task.stage_id, self.env.ref("hansbuyck_workflow.task_stage_te_plannen"))
        self.assertEqual(task.partner_id, self.partner)
        self.assertTrue(task.activity_ids, "to-do to plan the execution")
        self.assertEqual(set(projects.type_ids.mapped("name")), {"Te plannen", "Ingepland", "In uitvoering", "Opgeleverd"})
        return projects, task

    def test_confirm_with_installation_service(self):
        order = self._order([self.goods, self.plaatsing])
        order.action_confirm()
        self._assert_execution_project(order)

    def test_confirm_without_service_fallback(self):
        order = self._order([self.goods])
        order.action_confirm()
        self._assert_execution_project(order)

    def test_no_duplicate_on_reconfirm(self):
        order = self._order([self.goods])
        order.action_confirm()
        project = order.project_id
        order._action_cancel()
        order.action_draft()
        order.action_confirm()
        self.assertEqual(order.project_id, project)
        self.assertEqual(len(project.tasks.filtered(lambda t: t.name == "Uitvoering van de werken")), 1)

    def test_draft_quotation_has_no_project(self):
        order = self._order([self.goods, self.plaatsing])
        self.assertFalse(order.project_id)
        self.assertFalse(self.env["project.project"].search([("name", "ilike", order.name)]))

    def _opportunity(self):
        return self.env["crm.lead"].create({
            "name": "Offerte nieuwe ramen",
            "type": "opportunity",
            "partner_id": self.partner.id,
            "team_id": self.env.ref("hansbuyck_workflow.crm_team_website").id,
        })

    def test_confirm_marks_opportunity_won(self):
        lead = self._opportunity()
        order = self._order([self.goods, self.plaatsing])
        order.opportunity_id = lead
        self.assertEqual(lead.won_status, "pending")
        order.action_confirm()
        self.assertEqual(lead.won_status, "won")
        self.assertTrue(lead.stage_id.is_won)
        self.assertEqual(lead.probability, 100)

    def test_confirm_reopens_lost_opportunity_as_won(self):
        lead = self._opportunity()
        order = self._order([self.goods])
        order.opportunity_id = lead
        lead.action_set_lost()
        self.assertEqual(lead.won_status, "lost")
        order.action_confirm()
        self.assertTrue(lead.active)
        self.assertEqual(lead.won_status, "won")

    def test_quotation_alone_does_not_win(self):
        lead = self._opportunity()
        self._order([self.goods]).opportunity_id = lead
        self.assertEqual(lead.won_status, "pending")

    def test_template_untouched(self):
        self._order([self.goods]).action_confirm()
        self.assertTrue(self.template.is_template)
        self.assertEqual(len(self.template.tasks), 1)


@tagged("post_install", "-at_install")
class TestHansBuyckWebsiteForm(HttpCase):

    def test_website_form_creates_opportunity(self):
        website = self.env.ref("base.default_website")
        self.assertEqual(website.crm_default_team_id, self.env.ref("hansbuyck_workflow.crm_team_website"))
        self.authenticate(None, None)
        res = self.url_open("/website/form/crm.lead", data={
            "contact_name": "Jan Peeters",
            "email_from": "jan@example.com",
            "phone": "0470 00 00 00",
            "name": "Offerte nieuwe ramen",
            "description": "5 ramen in PVC",
            "csrf_token": self.csrf_token(),
        })
        self.assertEqual(res.status_code, 200, res.text)
        lead = self.env["crm.lead"].search([("email_from", "=", "jan@example.com")])
        self.assertEqual(len(lead), 1)
        self.assertEqual(lead.type, "opportunity")
        self.assertEqual(lead.team_id, self.env.ref("hansbuyck_workflow.crm_team_website"))
