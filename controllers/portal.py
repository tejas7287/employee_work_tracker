from odoo import http
from odoo.http import request
from werkzeug.utils import redirect


class WorkTaskPortal(http.Controller):

    # ---------------------------
    # TASK LIST PAGE
    # ---------------------------
    @http.route('/my/tasks', type='http', auth='user', website=True)
    def portal_my_tasks(self, **kw):

        user = request.env.user

        if user.has_group('base.group_system'):
            # ADMIN → see ALL tasks
            tasks = request.env['employee.work.task'].sudo().search([])
        else:
            # NORMAL USER → only own tasks
            tasks = request.env['employee.work.task'].sudo().search([
                ('employee_id.user_id', '=', user.id)
            ])

        return request.render(
            "employee_work_tracker.portal_my_tasks",
            {'tasks': tasks}
        )

    # ---------------------------
    # TASK DETAIL PAGE
    # ---------------------------
    @http.route('/my/task/<int:task_id>', type='http', auth='user', website=True)
    def portal_task_detail(self, task_id, **kw):

        user = request.env.user
        task = request.env['employee.work.task'].sudo().browse(task_id)

        if not task:
            return redirect('/my/tasks')

        if not user.has_group('base.group_system'):
            if task.employee_id.user_id.id != user.id:
                return redirect('/my/tasks')

        return request.render(
            "employee_work_tracker.portal_task_detail",
            {'task': task}
        )

    # ---------------------------
    # APPROVE TASK
    # ---------------------------
    @http.route('/my/task/approve/<int:task_id>', type='http', auth='user', website=True)
    def portal_task_approve(self, task_id, **kw):

        user = request.env.user
        task = request.env['employee.work.task'].sudo().browse(task_id)

        if task:
            if user.has_group('base.group_system') or task.employee_id.user_id.id == user.id:
                task.action_approve()

        return redirect(f'/my/task/{task_id}')

    # ---------------------------
    # REJECT TASK
    # ---------------------------
    @http.route('/my/task/reject/<int:task_id>', type='http', auth='user', website=True)
    def portal_task_reject(self, task_id, **kw):

        user = request.env.user
        task = request.env['employee.work.task'].sudo().browse(task_id)

        if task:
            if user.has_group('base.group_system') or task.employee_id.user_id.id == user.id:
                task.action_reject()

        return redirect(f'/my/task/{task_id}')

    # ---------------------------
    # PRINT TASK REPORT
    # ---------------------------
    @http.route('/my/task/print/<int:task_id>', type='http', auth='user', website=True)
    def portal_task_print(self, task_id, **kw):

        user = request.env.user
        task = request.env['employee.work.task'].sudo().browse(task_id)

        if not task:
            return redirect('/my/tasks')

        if not user.has_group('base.group_system'):
            if task.employee_id.user_id.id != user.id:
                return redirect('/my/tasks')

        report = request.env.ref('employee_work_tracker.action_task_report')

        return redirect(
            f'/report/pdf/{report.report_name}/{task.id}'
        )

    @http.route('/my/tasks', type='http', auth='user', website=True)
    def portal_my_tasks(self, **kw):

        user = request.env.user
        search = kw.get('search', '')
        sort = kw.get('sort', 'latest')

        domain = []

        # Role-based access
        if not user.has_group('base.group_system'):
            domain.append(('employee_id.user_id', '=', user.id))

        # Search filter
        if search:
            domain.append(('reference', 'ilike', search))

        # Sorting logic
        if sort == 'oldest':
            order = 'create_date asc'
        else:
            order = 'create_date desc'  # default latest

        tasks = request.env['employee.work.task'].sudo().search(domain, order=order)

        return request.render(
            "employee_work_tracker.portal_my_tasks",
            {
                'tasks': tasks,
                'search': search,
                'sort': sort,
            }
        )