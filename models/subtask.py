from odoo import models, fields
from odoo.exceptions import UserError


class EmployeeWorkSubtask(models.Model):
    _name = 'employee.work.subtask'
    _description = 'Employee Work Subtask'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)

    task_id = fields.Many2one(
        'employee.work.task',
        required=True,
        ondelete="cascade"
    )

    employee_id = fields.Many2one('hr.employee')

    start_date = fields.Date()
    end_date = fields.Date()
    hours_spent = fields.Float()

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft')

    approval_request_id = fields.Many2one(
        'approval.request',
        string="Approval Request"
    )

    def action_send_for_approval(self):
        category = self.env.ref(
            'employee_work_tracker.approval_category_subtask'
        )

        manager_user = self.task_id.manager_id.user_id

        # fallback if manager has no user
        if not manager_user:
            manager_user = self.env.user

        approval = self.env['approval.request'].create({
            'name': f"Subtask Approval: {self.name}",
            'request_owner_id': self.env.user.id,
            'category_id': category.id,
            'reason': f"Approval needed for subtask {self.name}",
            'approver_ids': [(0, 0, {
                'user_id': manager_user.id,
                'required': True
            })]
        })

        approval.action_confirm()

        self.write({
            'approval_request_id': approval.id,
            'state': 'waiting'
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Approval Review',
            'res_model': 'approval.request',
            'view_mode': 'form',
            'res_id': approval.id,
            'target': 'current',
        }

    def action_send_for_approval(self):

        category = self.env.ref(
            'employee_work_tracker.approval_category_subtask'
        )

        manager_user = self.task_id.manager_id.user_id

        if not manager_user:
            manager_user = self.env.user

        approval = self.env['approval.request'].sudo().create({
            'name': f"Subtask Approval: {self.name}",
            'request_owner_id': self.env.user.id,
            'category_id': category.id,
            'reason': f"Approval needed for subtask {self.name}",
            'approver_ids': [(0, 0, {
                'user_id': manager_user.id,
                'required': True
            })]
        })

        approval.sudo().action_confirm()

        self.write({
            'approval_request_id': approval.id,
            'state': 'waiting'
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Approval Review',
            'res_model': 'approval.request',
            'view_mode': 'form',
            'res_id': approval.id,
            'target': 'current',
        }