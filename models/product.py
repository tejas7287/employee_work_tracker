from odoo import models, fields
class ProductProduct(models.Model):
    _inherit = "product.product"

    def action_view_tasks(self):
        self.ensure_one()
        return self.product_tmpl_id.action_view_tasks()


class ProductTemplate(models.Model):
    _inherit = "product.template"

    task_count = fields.Integer(
        string="Tasks",
        compute="_compute_task_count"
    )

    def _compute_task_count(self):
        Task = self.env['employee.work.task']

        for product in self:
            tasks = Task.search([
                ('order_line_ids.product_id.product_tmpl_id', '=', product.id)
            ])
            product.task_count = len(tasks)

    def action_view_tasks(self):

        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Tasks',
            'res_model': 'employee.work.task',
            'view_mode': 'list,form',
            'domain': [
                ('order_line_ids.product_id.product_tmpl_id', '=', self.id)
            ],
        }
