from odoo import models


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    def action_approve(self):

        res = super().action_approve()

        subtasks = self.env['employee.work.subtask'].search([
            ('approval_request_id', '=', self.id)
        ])

        subtasks.write({
            'state': 'approved'
        })

        return res


    def action_refuse(self):

        res = super().action_refuse()

        subtasks = self.env['employee.work.subtask'].search([
            ('approval_request_id', '=', self.id)
        ])

        subtasks.write({
            'state': 'rejected'
        })

        return res