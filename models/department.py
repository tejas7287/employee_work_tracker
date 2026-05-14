from odoo import models, fields

class WorkDepartment(models.Model):
    _name = 'work.department'
    _description = 'Work Department'

    name = fields.Char(required=True)

    # Link to Contacts
    partner_id = fields.Many2one(
        'res.partner',
        string="Contact"
    )

    # Employees in this department
    employee_ids = fields.Many2many(
        'hr.employee',
        string="Employees"
    )