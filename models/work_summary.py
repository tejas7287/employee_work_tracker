from odoo import models, fields


class EmployeeWorkSummary(models.Model):
    _name = 'employee.work.summary'
    _description = 'Employee Work Summary'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True
    )

    total_tasks = fields.Integer(
        string='Total Tasks',
        default=0
    )

    total_hours = fields.Float(
        string='Total Hours',
        default=0.0
    )