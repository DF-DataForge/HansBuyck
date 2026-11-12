from odoo import api, models


class PlanningSlot(models.Model):
    _inherit = "planning.slot"

    @api.model_create_multi
    def create(self, vals_list):
        slots = super().create(vals_list)
        slots._hb_sync_execution_task()
        return slots

    def write(self, vals):
        res = super().write(vals)
        if {"resource_id", "start_datetime", "end_datetime", "project_id"} & set(vals):
            self._hb_sync_execution_task()
        return res

    def _hb_project(self):
        self.ensure_one()
        if "project_id" in self._fields and self.project_id:
            return self.project_id
        order = False
        if "sale_line_id" in self._fields and self.sale_line_id:
            order = self.sale_line_id.order_id
        elif "sale_order_id" in self._fields and self.sale_order_id:
            order = self.sale_order_id
        return order.project_id if order else self.env["project.project"]

    def _hb_sync_execution_task(self):
        """A shift with a fitter and a date plans the execution task."""
        for slot in self.sudo():
            if not (slot.resource_id and slot.start_datetime):
                continue
            project = slot._hb_project()
            if not project:
                continue
            tasks = project.tasks._hb_execution_tasks()
            if not tasks:
                continue
            vals = {}
            if "planned_date_begin" in tasks._fields:
                vals["planned_date_begin"] = slot.start_datetime
                vals["date_deadline"] = slot.end_datetime
            user = slot.resource_id.user_id
            for task in tasks:
                task_vals = dict(vals)
                if user and user not in task.user_ids:
                    task_vals["user_ids"] = [(4, user.id)]
                task.write(task_vals)
            tasks._hb_move_to_planned()
