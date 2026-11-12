from datetime import datetime, timedelta

from odoo.tests import TransactionCase, tagged

from ..models.planning_slot import END_FIELDS, RESOURCE_FIELDS, START_FIELDS


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
        Slot = cls.env["planning.slot"]
        cls.resource_field = Slot._hb_field(RESOURCE_FIELDS)
        cls.start_field = Slot._hb_field(START_FIELDS)
        cls.end_field = Slot._hb_field(END_FIELDS)
        comodel = Slot._fields[cls.resource_field].comodel_name if cls.resource_field else None
        if comodel == "res.users":
            cls.fitter = cls.fitter_user
        elif comodel == "hr.employee":
            cls.fitter = cls.env["hr.employee"].create({"name": "Plaatser Piet", "user_id": cls.fitter_user.id})
        elif comodel:
            cls.fitter = cls.env[comodel].create({"name": "Plaatser Piet", "user_id": cls.fitter_user.id})

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
        self.assertTrue(self.resource_field and self.start_field, "planning.slot fields not recognised, see install log")
        slot = order._hb_order_slots()[:1]
        vals = {self.resource_field: self.fitter.id, self.start_field: start}
        if self.end_field:
            vals[self.end_field] = start + timedelta(hours=8)
        slot.write(vals)
        self.assertEqual(task.stage_id, self.planned)
        self.assertIn(self.fitter_user, task.user_ids)
        self.assertEqual(task.planned_date_begin, start)

    def test_unassigned_slot_does_not_crash_or_plan(self):
        """Regression: creating shifts (as Sales Planning does) must never raise."""
        order = self._confirmed([(self.goods, 1), (self.plaatsing, 1)])
        self.assertEqual(self._task(order).stage_id, self.todo)

    def test_gantt_planning_moves_task(self):
        order = self._confirmed([(self.goods, 1)])
        task = self._task(order)
        start = datetime.now().replace(microsecond=0) + timedelta(days=5)
        task.write({"planned_date_begin": start, "date_deadline": start + timedelta(hours=8)})
        self.assertEqual(task.stage_id, self.planned)
