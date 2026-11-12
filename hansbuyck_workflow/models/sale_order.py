from datetime import timedelta

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_confirm(self):
        res = super()._action_confirm()
        self.sudo()._hb_mark_opportunity_won()
        if not self.env.context.get("disable_project_task_generation"):
            self.sudo()._hb_ensure_execution_project()
        return res

    def _hb_mark_opportunity_won(self):
        """A confirmed quotation wins its opportunity (also if it was marked lost)."""
        for order in self:
            lead = order.opportunity_id
            if lead and lead.won_status != "won":
                lead.action_set_won()
                lead.message_post(body=self.env._("Marked as won: quotation %s was confirmed.", order._get_html_link()))

    def _hb_ensure_execution_project(self):
        """Every confirmed quotation gets an execution project.

        Quotations containing the "Plaatsing ramen en deuren" service already got
        their project from standard Odoo (service tracking + project template).
        For the others we create it here from the same template, so no order
        slips through. Afterwards the execution task gets a to-do to plan it.
        """
        template = self.env.ref("hansbuyck_workflow.project_template_uitvoering", raise_if_not_found=False)
        if not template:
            return
        for order in self:
            if not (order.project_id or order.order_line.project_id):
                order._hb_create_project_from_template(template)
            projects = order.project_id | order.order_line.project_id
            if projects and not projects.user_id and order.user_id:
                projects.filtered(lambda p: not p.user_id).user_id = order.user_id
            order._hb_schedule_planning_activity(projects)

    def _hb_create_project_from_template(self, template):
        self.ensure_one()
        partner = self.partner_id
        name = "%s - %s" % (self.name, partner.commercial_company_name or partner.name)
        account = self.env["account.analytic.account"].create(self._prepare_analytic_account_data())
        project = template.action_create_from_template({
            "name": name,
            "partner_id": partner.id,
            "company_id": self.company_id.id,
            "account_id": account.id,
            "user_id": template.user_id.id or self.user_id.id,
            "allow_billable": True,
        })
        project.reinvoiced_sale_order_id = self
        project.tasks.write({"partner_id": partner.id})
        self.project_id = project
        project.message_post(body=self.env._("Project created on confirmation of %s.", self._get_html_link()))
        return project

    def _hb_schedule_planning_activity(self, projects):
        tag = self.env.ref("hansbuyck_workflow.project_tag_uitvoering", raise_if_not_found=False)
        tasks = projects.tasks
        if tag:
            tasks = tasks.filtered(lambda t: tag in t.tag_ids)
        todo = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        for task in tasks.filtered(lambda t: not t.activity_ids):
            user = task.project_id.user_id or self.user_id or self.env.user
            task.partner_id = task.partner_id or self.partner_id
            task.activity_schedule(
                activity_type_id=todo.id if todo else False,
                summary=self.env._("Uitvoering inplannen"),
                note=self.env._("Offerte %s is bevestigd: plan de uitvoering in (datum en plaatsers).", self.name),
                user_id=user.id,
                date_deadline=fields.Date.context_today(self) + timedelta(days=2),
            )
