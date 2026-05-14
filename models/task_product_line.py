from odoo import models, fields
class TaskProductLine(models.Model):
    _name = 'employee.work.task.line'
    _description = 'Task Product Line'

    task_id = fields.Many2one(
        'employee.work.task',
        ondelete='cascade'
    )

    product_id = fields.Many2one(
        'product.product',
        string="Product",
        required=True
    )

    quantity = fields.Float(
        string="Quantity",
        default=1
    )

    price_unit = fields.Float(
        string="Unit Price"
    )