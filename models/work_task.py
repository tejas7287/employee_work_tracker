from odoo import models, fields, api
from markupsafe import Markup
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import logging
import base64
import qrcode
from io import BytesIO

_logger = logging.getLogger(__name__)


class EmployeeWorkTask(models.Model):
    _name = 'employee.work.task'
    _description = 'Employee Work Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc'
    _rec_name = 'reference'
    _sql_constraints = [
        ('reference_unique', 'unique(reference)', 'Reference must be unique!')
    ]

    reference = fields.Char(
        string="Reference",
        readonly=True,
        copy=False,
        default="New"
    )
    department_id = fields.Many2one(
        'work.department',
        string="Department"
    )

    employee_ids = fields.Many2many(
        'hr.employee',
        string="Employees"
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Customer"
    )

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order"
    )

    order_line_ids = fields.One2many(
        'employee.work.task.line',
        'task_id',
        string="Product Lines"
    )



    name = fields.Char(string='Task Title', required=True, tracking=True)

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        tracking=True
    )

    description = fields.Text(string='Description' ,tracking=True)

    start_date = fields.Date(
        string='Start Date',
        default=fields.Date.context_today
    )

    end_date = fields.Date(string='End Date')

    hours_spent = fields.Float(
        string='Hours Spent',
        tracking=True
    )

    manager_id = fields.Many2one(
        'hr.employee',
        string='Manager',
        tracking=True
    )

    password = fields.Char(
        string='Password'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft', tracking=True)

    # -------------------------
    # REMINDER FLAGS
    # -------------------------

    reminder_7_sent = fields.Boolean(default=False)
    reminder_3_sent = fields.Boolean(default=False)
    reminder_1_sent = fields.Boolean(default=False)

    # -------------------------
    # WORKFLOW METHODS
    # -------------------------

    def action_approve(self):
        for task in self:

            pending_subtasks = task.subtask_ids.filtered(
                lambda s: s.state not in ('approved', 'rejected')
            )

            if pending_subtasks:
                raise ValidationError(
                    "All subtasks must be Approved or Rejected before approving the task."
                )

            task.state = 'approved'

    def action_reject(self):
        for task in self:

            pending_subtasks = task.subtask_ids.filtered(
                lambda s: s.state not in ('approved', 'rejected')
            )

            if pending_subtasks:
                raise ValidationError(
                    "All subtasks must be Approved or Rejected before rejecting the task."
                )

            task.state = 'rejected'

    # -------------------------
    # SUMMARY HELPER
    # -------------------------

    def _update_employee_summary(self, employee_id, task_delta, hours_delta):

        if not employee_id:
            return

        summary = self.env['employee.work.summary'].search(
            [('employee_id', '=', employee_id)],
            limit=1
        )

        if summary:
            summary.write({
                'total_tasks': summary.total_tasks + task_delta,
                'total_hours': summary.total_hours + hours_delta
            })

        elif task_delta > 0:
            self.env['employee.work.summary'].create({
                'employee_id': employee_id,
                'total_tasks': task_delta,
                'total_hours': hours_delta
            })

    # -------------------------
    # CREATE
    # -------------------------

    @api.model_create_multi
    def create(self, vals_list):

        # Generate unique reference
        for vals in vals_list:
            if vals.get('reference', 'New') == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'employee.work.task.seq'
                ) or 'New'

        tasks = super(EmployeeWorkTask, self).create(vals_list)

        template = self.env.ref(
            'employee_work_tracker.email_template_deadline',
            raise_if_not_found=False
        )

        for task in tasks:

            # update summary
            self._update_employee_summary(
                task.employee_id.id,
                1,
                task.hours_spent
            )

            # add manager follower
            if task.manager_id and task.manager_id.user_id:
                task.message_subscribe(
                    partner_ids=[task.manager_id.user_id.partner_id.id]
                )

            # send mail
            if template:
                template.send_mail(task.id, force_send=True)

        return tasks

    # -------------------------
    # WRITE
    # -------------------------

    def write(self, vals):

        for record in self:

            old_employee_id = record.employee_id.id
            old_hours = record.hours_spent

            super(EmployeeWorkTask, record).write(vals)

            if 'employee_id' in vals or 'hours_spent' in vals:

                new_hours = vals.get('hours_spent', old_hours)
                new_employee_id = vals.get('employee_id', old_employee_id)

                if old_employee_id == new_employee_id:

                    self._update_employee_summary(
                        old_employee_id,
                        0,
                        new_hours - old_hours
                    )

                else:

                    self._update_employee_summary(
                        old_employee_id,
                        -1,
                        -old_hours
                    )

                    self._update_employee_summary(
                        new_employee_id,
                        1,
                        new_hours
                    )

        return True

    # -------------------------
    # DELETE
    # -------------------------

    def unlink(self):

        for task in self:
            self._update_employee_summary(
                task.employee_id.id,
                -1,
                -task.hours_spent
            )

        return super(EmployeeWorkTask, self).unlink()

    # -------------------------
    # CRON JOB
    # -------------------------

    @api.model
    def _cron_send_deadline_reminder(self):

        today = fields.Date.today()

        tasks = self.search([
            ('end_date', '!=', False),
            ('state', '=', 'draft')
        ])

        Mail = self.env['mail.mail']

        for task in tasks:

            days_left = (task.end_date - today).days

            # -------------------------
            # BEFORE DEADLINE (7,3,1)
            # -------------------------
            if days_left in [7, 3, 1]:

                body = f"""
                <p><b>Task Deadline Reminder</b></p>

                <p>The following task is approaching its deadline.</p>

                <table border="0" cellpadding="4" cellspacing="0">
                <tr>
                    <td><b>Task</b></td>
                    <td>: {task.name}</td>
                </tr>
                <tr>
                    <td><b>Employee</b></td>
                    <td>: {task.employee_id.name}</td>
                </tr>
                <tr>
                    <td><b>Manager</b></td>
                    <td>: {task.manager_id.name or '-'}</td>
                </tr>
                <tr>
                    <td><b>Deadline</b></td>
                    <td>: {task.end_date}</td>
                </tr>
                <tr>
                    <td><b>Days Remaining</b></td>
                    <td>: {days_left}</td>
                </tr>
                </table>

                <br/>

                <p>Please ensure the task is completed before the deadline.</p>

                <p>
                Regards,<br/>
                <b>{self.env.company.name}</b>
                </p>
                """

                # chatter message
                task.message_post(
                    body=Markup(body),
                    subject="Task Deadline Reminder",
                    subtype_xmlid="mail.mt_comment"
                )

                # send email to employee
                if task.employee_id.work_email:
                    Mail.create({
                        'subject': "Task Deadline Reminder",
                        'body_html': body,
                        'email_to': task.employee_id.work_email,
                        'email_from': self.env.company.email,
                        'auto_delete': False,
                    })

            # -------------------------
            # AFTER DEADLINE
            # -------------------------
            elif days_left < 0:

                overdue_days = abs(days_left)

                body = f"""
                <p><b>Task Overdue Alert</b></p>

                <p>The following task is overdue.</p>

                <table border="0" cellpadding="4" cellspacing="0">
                <tr>
                    <td><b>Task</b></td>
                    <td>: {task.name}</td>
                </tr>
                <tr>
                    <td><b>Employee</b></td>
                    <td>: {task.employee_id.name}</td>
                </tr>
                <tr>
                    <td><b>Deadline</b></td>
                    <td>: {task.end_date}</td>
                </tr>
                <tr>
                    <td><b>Overdue By</b></td>
                    <td>: {overdue_days} days</td>
                </tr>
                </table>

                <br/>

                <p>Please complete the task as soon as possible.</p>

                <p>
                Regards,<br/>
                <b>{self.env.company.name}</b>
                </p>
                """

                task.message_post(
                    body=Markup(body),
                    subject="Task Overdue Reminder",
                    subtype_xmlid="mail.mt_comment"
                )

                if task.employee_id.work_email:
                    Mail.create({
                        'subject': "Task Overdue Reminder",
                        'body_html': body,
                        'email_to': task.employee_id.work_email,
                        'email_from': self.env.company.email,
                        'auto_delete': False,
                    })

    def action_print_task_report(self):
        return self.env.ref(
            'employee_work_tracker.action_task_report'
        ).report_action(self)

    # -------------------------
    # SUBTASK SUPPORT
    # -------------------------

    subtask_ids = fields.One2many(
        'employee.work.subtask',
        'task_id',
        string='Subtasks'
    )

    subtask_count = fields.Integer(
        string="Subtasks",
        compute="_compute_subtask_count"
    )

    @api.depends('subtask_ids')
    def _compute_subtask_count(self):
        for rec in self:
            rec.subtask_count = len(rec.subtask_ids)

    def action_view_subtasks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Subtasks',
            'res_model': 'employee.work.subtask',
            'view_mode': 'list,form',
            'domain': [('task_id', '=', self.id)],
            'context': {'default_task_id': self.id},
        }

    sale_order_count = fields.Integer(
        string="Sale Orders",
        compute="_compute_sale_order_count"
    )

    @api.depends('sale_order_id')
    def _compute_sale_order_count(self):
        for rec in self:
            rec.sale_order_count = 1 if rec.sale_order_id else 0

    def action_view_sale_order(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
            'target': 'current',
        }

    product_ids = fields.Many2many(
        'product.product',
        compute='_compute_products',
        string="Products"
    )

    @api.depends('order_line_ids.product_id')
    def _compute_products(self):
        for rec in self:
            rec.product_ids = rec.order_line_ids.mapped('product_id')

    product_count = fields.Integer(
        compute="_compute_products",
        string="Products"
    )

    @api.depends('order_line_ids.product_id')
    def _compute_products(self):
        for rec in self:
            products = rec.order_line_ids.mapped('product_id')
            rec.product_ids = products
            rec.product_count = len(products)

    def action_view_products(self):

        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Products',
            'res_model': 'product.product',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.product_ids.ids)],
        }



    # Many2many links for the Smart Buttons
    sale_order_ids = fields.Many2many(
        'sale.order',
        'sale_order_task_rel',  # Changed name slightly to avoid old SQL conflicts
        'task_id',
        'order_id',
        string="Sales Orders"
    )

    purchase_order_ids = fields.Many2many(
        'purchase.order',
        'purchase_task_rel',
        'task_id',
        'purchase_id',
        string="Purchase Orders"
    )

    mrp_ids = fields.Many2many(
        'mrp.production',
        'mrp_task_rel',
        'task_id',
        'production_id',
        string="Manufacturing Orders"
    )

    crm_ids = fields.Many2many(
        'crm.lead',
        'crm_lead_task_rel',
        'task_id',
        'lead_id',
        string="CRM Opportunities"
    )

    # =========================
    # COUNTS FOR SMART BUTTONS
    # =========================
    # Note: store=True is fine, but you MUST re-save the record to trigger it
    sale_count = fields.Integer(string="Sales", compute="_compute_link_counts")
    purchase_count = fields.Integer(string="Purchases", compute="_compute_link_counts")
    mrp_count = fields.Integer(string="Manufacturing", compute="_compute_link_counts")
    crm_count = fields.Integer(string="CRM", compute="_compute_link_counts")

    @api.depends('sale_order_ids', 'purchase_order_ids', 'mrp_ids', 'crm_ids')
    def _compute_link_counts(self):

        for rec in self:
            rec.sale_count = len(rec.sale_order_ids)

            rec.purchase_count = len(rec.purchase_order_ids)

            rec.mrp_count = len(rec.mrp_ids)

            rec.crm_count = len(rec.crm_ids)

    @api.onchange('sale_order_id')
    def _onchange_sale_order(self):
        if self.sale_order_id:
            self.sale_order_ids = [(4, self.sale_order_id.id)]
    # ==========================================
    # UPDATED ACTION TO REFRESH COUNTER
    # ==========================================
    def action_confirm_sale(self):

        for task in self:

            if not task.partner_id:
                raise ValidationError("Please select a customer.")

            if not task.order_line_ids:
                raise ValidationError("Add at least one product.")

            order = self.env['sale.order'].create({
                'partner_id': task.partner_id.id,
                'order_line': [(0, 0, {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'price_unit': line.price_unit,
                }) for line in task.order_line_ids]
            })

            order.action_confirm()

            task.sale_order_id = order.id
            task.sale_order_ids = [(4, order.id)]
    # =========================
    # SMART BUTTON ACTIONS
    # =========================

    def action_view_sales(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sales Orders',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.sale_order_ids.ids)],
            'context': {'default_partner_id': self.partner_id.id},
        }

    def action_view_purchase(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.purchase_order_ids.ids)],
        }

    def action_view_mrp(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Manufacturing Orders',
            'res_model': 'mrp.production',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.mrp_ids.ids)],
        }

    def action_view_crm(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'CRM Opportunities',
            'res_model': 'crm.lead',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.crm_ids.ids)],
        }



    qr_code = fields.Binary("QR Code", compute="_compute_qr_code")
    qr_url = fields.Char(string="QR URL", compute="_compute_qr_url")

    def _compute_qr_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            rec.qr_url = f"{base_url}/task/details/{rec.id}"

    def _compute_qr_code(self):
        for rec in self:
            if rec.qr_url:
                qr = qrcode.make(rec.qr_url)
                buffer = BytesIO()
                qr.save(buffer, format="PNG")
                rec.qr_code = base64.b64encode(buffer.getvalue())

    # -------------------------
    # DOCUMENT SUPPORT
    # -------------------------

    document_ids = fields.One2many(
        'task.document',
        'task_id',
        string="Documents"
    )

    document_count = fields.Integer(
        string="Documents",
        compute="_compute_document_count"
    )

    @api.depends('document_ids')
    def _compute_document_count(self):
        for rec in self:
            rec.document_count = len(rec.document_ids)

    def action_view_documents(self):
        self.ensure_one()

        return {
            'name': 'Documents',
            'type': 'ir.actions.act_window',
            'res_model': 'task.document',
            'view_mode': 'list,form',
            'domain': [('task_id', '=', self.id)],
            'context': {'default_task_id': self.id},
            'target': 'current',
        }

    allowed_employee_ids = fields.Many2many(
        'hr.employee',
        compute='_compute_allowed_employees'
    )

    @api.depends('department_id')
    def _compute_allowed_employees(self):
        for rec in self:
            if rec.department_id:
                rec.allowed_employee_ids = rec.department_id.employee_ids
            else:
                rec.allowed_employee_ids = False

    @api.onchange('employee_ids')
    def _onchange_employee_ids(self):
        if self.employee_ids:
            self.employee_id = self.employee_ids[0]

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'