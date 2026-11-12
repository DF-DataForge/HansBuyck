from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def _hb_execution_tasks(self):
        tag = self.env.ref("hansbuyck_workflow.project_tag_uitvoering", raise_if_not_found=False)
        return self.filtered(lambda t: tag in t.tag_ids) if tag else self.browse()

    def _hb_move_to_planned(self):
        todo = self.env.ref("hansbuyck_workflow.task_stage_te_plannen", raise_if_not_found=False)
        planned = self.env.ref("hansbuyck_workflow.task_stage_ingepland", raise_if_not_found=False)
        if not (todo and planned):
            return
        tasks = self.filtered(lambda t: t.stage_id == todo)
        if tasks:
            tasks.write({"stage_id": planned.id})

    def write(self, vals):
        res = super().write(vals)
        # Planned in the Gantt view (project_enterprise) -> "Ingepland"
        if vals.get("planned_date_begin") and "stage_id" not in vals:
            self._hb_execution_tasks()._hb_move_to_planned()
        return res
