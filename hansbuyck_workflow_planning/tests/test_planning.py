from datetime import datetime, timedelta

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHansBuyckPlanning(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Klant Planning"})
        cls.goods = cls.env["product.product"].create({"name": "Alu raam", "type": "consu", "list_price": 900})
        cls.plaatsing = cls.env.ref("hansbuyck_workflow.product_plaatsing").product_variant_id
        cls.role = cls.env.ref("hansbuyck_workflow_planning.planning_role_plaatser")
        cls.todo = cls.env.ref("hansbuyck_workflow.task_stage_te_plannen")
        cls.planned = cls.env.ref("hansbuyck_workflow.task_stage_ingepland")
        cls.fitter_user = cls.env["res.users"].create({"name": "Plaatser Piet", "login": "plaatser_piet"})
        cls.fitter = cls.env["resource.resource"].create({"name": "Plaatser Piet", "user_id": cls.fitter_user.id})

    def _confirmed(self, lines):
        order = self.env["sale.order"].create({
            "partner_id": self.partner.id,
            "order_line": [(0, 0, {"product_id": p.id, "product_uom_qty": q}) for p, q in lines],
        })
        order.action_confirm()
        return order

    def _task(self, order):
        return order.project_id.tasks._hb_execution_tasks()

    def test_product_configured(self):
        tmpl = self.plaatsing.product_tmpl_id
        self.assertEqual(tmpl.uom_id, self.env.ref("uom.product_uom_day"))
        self.assertTrue(tmpl.planning_enabled)
        self.assertEqual(tmpl.planning_role_id, self.role)

    def test_confirm_with_service_creates_slot(self):
        order = self._confirmed([(self.goods, 5), (self.plaatsing, 2)])
        slots = order._hb_order_slots()
        self.assertTrue(slots, "Sales Planning creates a shift to plan")
        self.assertEqual(slots.role_id, self.role)
        self.assertAlmostEqual(sum(slots.mapped("allocated_hours")), 16.0, msg="2 days = 16 hours")
        self.assertEqual(len(self._task(order)), 1)

    def test_confirm_without_service_fallback_slot(self):
        order = self._confirmed([(self.goods, 3)])
        slots = order._hb_order_slots() or self.env["planning.slot"].search([("name", "ilike", order.name)])
        self.assertEqual(len(slots), 1)
        self.assertEqual(slots.role_id, self.role)

    def test_assign_slot_plans_task(self):
        order = self._confirmed([(self.goods, 1), (self.plaatsing, 1)])
        task = self._task(order)
        self.assertEqual(task.stage_id, self.todo)
        start = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=3)
        slot = order._hb_order_slots()[:1]
        slot.write({"resource_id": self.fitter.id, "start_datetime": start, "end_datetime": start + timedelta(hours=8)})
        self.assertEqual(task.stage_id, self.planned)
        self.assertIn(self.fitter_user, task.user_ids)
        self.assertEqual(task.planned_date_begin, start)

    def test_gantt_planning_moves_task(self):
        order = self._confirmed([(self.goods, 1)])
        task = self._task(order)
        start = datetime.now().replace(microsecond=0) + timedelta(days=5)
        task.write({"planned_date_begin": start, "date_deadline": start + timedelta(hours=8)})
        self.assertEqual(task.stage_id, self.planned)
