from odoo import http
from odoo.http import request


class TaskQRController(http.Controller):

    @http.route('/task/details/<int:task_id>', type='http', auth='public', website=True)
    def task_details(self, task_id, **kwargs):

        task = request.env['employee.work.task'].sudo().browse(task_id)

        # Handle invalid task id
        if not task.exists():
            return request.not_found()

        return request.render(
            'employee_work_tracker.task_qr_page',
            {
                'task': task
            }
        )