from odoo import models, fields, api


class TaskDocument(models.Model):
    _name = 'task.document'
    _description = 'Task Documents'
    _order = 'upload_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    task_id = fields.Many2one(
        'employee.work.task',
        string="Task",
        required=True,
        ondelete='cascade'
    )

    document_file = fields.Binary(
        string="File",
        attachment=True,
        required=True
    )

    # remove readonly so filename can be stored
    file_name = fields.Char(
        string="File Name"
    )

    uploaded_by = fields.Many2one(
        'res.users',
        string="Uploaded By",
        default=lambda self: self.env.user,
        readonly=True
    )

    upload_date = fields.Datetime(
        string="Uploaded On",
        default=fields.Datetime.now,
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):

        records = super().create(vals_list)

        for rec in records:

            filename = rec.file_name or "File"
            attachment = None

            # create attachment for chatter preview
            if rec.document_file and rec.task_id:

                attachment = self.env['ir.attachment'].create({
                    'name': filename,
                    'datas': rec.document_file,
                    'res_model': 'employee.work.task',
                    'res_id': rec.task_id.id,
                    'type': 'binary',
                })

                rec.file_name = attachment.name

            # post in chatter with preview
            if rec.task_id:
                rec.task_id.message_post(
                    body=f"📎 Document uploaded: {rec.file_name}",
                    attachment_ids=[attachment.id] if attachment else [],
                    subtype_xmlid="mail.mt_comment"
                )

        return records

    def unlink(self):

        for rec in self:

            filename = rec.file_name or "File"

            if rec.task_id:
                rec.task_id.message_post(
                    body=f"🗑 Document deleted: {filename}"
                )

        return super().unlink()