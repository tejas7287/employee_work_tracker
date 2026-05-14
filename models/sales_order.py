from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    task_ids = fields.Many2many(
        'employee.work.task',
        'sale_order_task_rel',
        'order_id',
        'task_id',
        string="Task References"
    )

    task_count = fields.Integer(
        string="Tasks",
        compute="_compute_task_count"
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
            'context': {'default_sale_order_id': self.id},
        }