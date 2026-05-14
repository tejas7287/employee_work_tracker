from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    task_ids = fields.Many2many(
        'employee.work.task',
        'purchase_task_rel',
        'purchase_id',
        'task_id',
        string="Task References"
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