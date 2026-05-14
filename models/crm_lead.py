from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = "crm.lead"

    task_ids = fields.Many2many(
        'employee.work.task',
        'crm_lead_task_rel',
        'lead_id',
        'task_id',
        string="Task Reference"
    )

    task_count = fields.Integer(
        compute="_compute_task_count",
        string="Tasks"
    )

    @api.depends('task_ids')
    def _compute_task_count(self):
        for rec in self:
            rec.task_count = len(rec.task_ids)

    def action_view_tasks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tasks',
            'res_model': 'employee.work.task',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.task_ids.ids)],
        }