import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

# Field names differ between Planning versions: use the first one that exists.
RESOURCE_FIELDS = ("resource_id", "employee_id", "user_id")
START_FIELDS = ("start_datetime", "start_date", "date_start")
END_FIELDS = ("end_datetime", "end_date", "date_end")


class PlanningSlot(models.Model):
    _inherit = "planning.slot"

    @api.model
    def _hb_field(self, candidates):
        return next((name for name in candidates if name in self._fields), None)

    @api.model_create_multi
    def create(self, vals_list):
        slots = super().create(vals_list)
        slots._hb_safe_sync_execution_task()
        return slots

    def write(self, vals):
        res = super().write(vals)
        watched = {self._hb_field(RESOURCE_FIELDS), self._hb_field(START_FIELDS), self._hb_field(END_FIELDS), "project_id"}
        if watched & set(vals):
            self._hb_safe_sync_execution_task()
        return res

    def _hb_safe_sync_execution_task(self):
        """Never let the task sync block saving a shift or confirming a quotation."""
        if self.env.context.get("hb_planning_sync"):
            return  # already syncing: avoid shift <-> task ping-pong
        self = self.with_context(hb_planning_sync=True)
        try:
            with self.env.cr.savepoint():
                self._hb_sync_execution_task()
        except Exception:
            _logger.exception("hansbuyck_workflow_planning: could not sync execution task for shifts %s", self.ids)

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

    def _hb_assigned_user(self, resource_field):
        """res.users of the planned fitter (resource, employee or user field)."""
        record = self[resource_field]
        if record._name == "res.users":
            return record
        return record.user_id if "user_id" in record._fields else self.env["res.users"]

    def _hb_sync_execution_task(self):
        """A shift with a fitter and a start date plans the execution task."""
        resource_field = self._hb_field(RESOURCE_FIELDS)
        start_field = self._hb_field(START_FIELDS)
        end_field = self._hb_field(END_FIELDS)
        if not (resource_field and start_field):
            _logger.warning(
                "hansbuyck_workflow_planning: planning.slot has none of %s / %s; task sync disabled",
                RESOURCE_FIELDS, START_FIELDS)
            return
        for slot in self.sudo():
            if not (slot[resource_field] and slot[start_field]):
                continue
            project = slot._hb_project()
            if not project:
                continue
            tasks = project.tasks._hb_execution_tasks()
            if not tasks:
                continue
            vals = {}
            if "planned_date_begin" in tasks._fields:
                vals["planned_date_begin"] = slot[start_field]
                if end_field and slot[end_field]:
                    vals["date_deadline"] = slot[end_field]
            users = slot._hb_assigned_user(resource_field)
            for task in tasks:
                task_vals = dict(vals)
                new_users = users - task.user_ids
                if new_users:
                    task_vals["user_ids"] = [(4, user.id) for user in new_users]
                if task_vals:
                    task.write(task_vals)
            tasks._hb_move_to_planned()
