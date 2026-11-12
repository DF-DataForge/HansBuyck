import logging
from datetime import datetime, time, timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)

HOURS_PER_DAY = 8.0


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_confirm(self):
        res = super()._action_confirm()
        if not self.env.context.get("disable_project_task_generation"):
            for order in self.sudo():
                order._hb_ensure_planning_slot()
        return res

    # ------------------------------------------------------------------ helpers
    def _hb_order_slots(self):
        Slot = self.env["planning.slot"]
        if "sale_line_id" in Slot._fields:
            return Slot.search([("sale_line_id", "in", self.order_line.ids)])
        if "sale_order_id" in Slot._fields:
            return Slot.search([("sale_order_id", "=", self.id)])
        return Slot

    def _hb_ensure_planning_slot(self):
        """Make sure a confirmed quotation has a shift to plan in Planning.

        Quotations with the installation service get theirs from Sales Planning;
        for the others we create one shift of one day for the role "Plaatser".
        """
        self.ensure_one()
        Slot = self.env["planning.slot"]
        slots = self._hb_order_slots()
        project = self.project_id
        if not slots:
            role = self.env.ref("hansbuyck_workflow_planning.planning_role_plaatser", raise_if_not_found=False)
            vals = {}
            if role and "role_id" in Slot._fields:
                vals["role_id"] = role.id
            if "allocated_hours" in Slot._fields:
                vals["allocated_hours"] = HOURS_PER_DAY
            if "name" in Slot._fields:
                vals["name"] = self.env._("Uitvoering %(order)s - %(partner)s", order=self.name, partner=self.partner_id.display_name)
            if "company_id" in Slot._fields:
                vals["company_id"] = self.company_id.id
            # "to plan" shifts have no dates, unless this version requires them
            if Slot._fields.get("start_datetime") and Slot._fields["start_datetime"].required:
                start = datetime.combine(fields.Date.context_today(self) + timedelta(days=1), time(8, 0))
                vals["start_datetime"] = start
                vals["end_datetime"] = start + timedelta(hours=HOURS_PER_DAY)
            try:
                with self.env.cr.savepoint():
                    slots = Slot.create(vals)
            except Exception:
                _logger.exception("Could not create planning shift for %s", self.name)
                self.message_post(body=self.env._(
                    "De shift voor de uitvoering kon niet automatisch aangemaakt worden. Maak ze manueel aan in Planning."))
                return
        if project and "project_id" in Slot._fields:
            slots.filtered(lambda s: not s.project_id).write({"project_id": project.id})
        return slots
