from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
# -------------------------------
# Serial Tracking Model
# -------------------------------
class MrpWorkorderLine(models.Model):
    _name = 'mrp.workorder.line'
    _description = 'Workorder Serial Tracking'

    workorder_id = fields.Many2one('mrp.workorder')
    production_id = fields.Many2one('mrp.production', ondelete='cascade')

    lot_id = fields.Many2one('stock.lot', string="Serial Number")

    employee_ids = fields.Many2many(
        'hr.employee',
        string="Employees Worked"
    )

    workcenter_id = fields.Many2one('mrp.workcenter')



# -------------------------------
# History Model
# -------------------------------
class MrpWorkorderHistory(models.Model):
    _name = 'mrp.workorder.history'
    _description = 'Workorder Serial History'

    production_id = fields.Many2one('mrp.production', ondelete='cascade')
    lot_id = fields.Many2one('stock.lot')

    employee_ids = fields.Many2many('hr.employee')

    workcenter_id = fields.Many2one('mrp.workcenter')
    workorder_id = fields.Many2one('mrp.workorder')


# -------------------------------
# Manufacturing Order
# -------------------------------
class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    workorder_line_count = fields.Integer(compute="_compute_workorder_line_count")
    history_count = fields.Integer(compute="_compute_history_count")

    def _compute_workorder_line_count(self):
        for rec in self:
            rec.workorder_line_count = self.env['mrp.workorder.line'].search_count([
                ('production_id', '=', rec.id)
            ])

    def _compute_history_count(self):
        for rec in self:
            rec.history_count = self.env['mrp.workorder.history'].search_count([
                ('production_id', '=', rec.id)
            ])

    # -------------------------------
    # SERIAL CREATION
    # -------------------------------

    def action_confirm(self):
        res = super().action_confirm()

        for production in self:

            if production.product_id.tracking != 'serial':
                continue

            existing = self.env['mrp.workorder.line'].search_count([
                ('production_id', '=', production.id)
            ])
            if existing:
                continue

            lines_vals = []

            for i in range(int(production.product_qty)):
                lot = self.env['stock.lot'].create({
                    'name': f"{production.name}-{i + 1}",
                    'product_id': production.product_id.id,
                    'production_id': production.id,
                })

                lines_vals.append({
                    'production_id': production.id,
                    'lot_id': lot.id,
                })

            self.env['mrp.workorder.line'].create(lines_vals)

        return res

    # -------------------------------
    # SMART BUTTONS
    # -------------------------------
    def action_view_serials(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Serial Tracking',
            'res_model': 'mrp.workorder.line',
            'view_mode': 'list,form',
            'domain': [('production_id', '=', self.id)],
        }

    def action_view_history(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Serial History',
            'res_model': 'mrp.workorder.history',
            'view_mode': 'list,form',
            'domain': [('production_id', '=', self.id)],
        }


# -------------------------------
# Workorder Logic
# -------------------------------
class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    workorder_line_ids = fields.One2many(
        'mrp.workorder.line',
        'workorder_id'
    )

    # -------------------------------
    # SAFE MOVE FUNCTION
    # -------------------------------
    def _move_lot(self, lot, source, destination, product=None, qty=1):
        if not source or not destination:
            return

        if source.id == destination.id:
            return

        product = product or (lot.product_id if lot else None)
        if not product:
            return

        if qty <= 0:
            return

        move = self.env['stock.move'].create({
            'name': f'Move {product.name}',
            'product_id': product.id,
            'product_uom_qty': qty,
            'product_uom': product.uom_id.id,
            'location_id': source.id,
            'location_dest_id': destination.id,
            'company_id': self.env.company.id,
        })

        move._action_confirm()
        move._action_assign()

        # If no move lines created → create manually
        if not move.move_line_ids:
            self.env['stock.move.line'].create({
                'move_id': move.id,
                'product_id': product.id,
                'qty_done': qty,
                'product_uom_id': product.uom_id.id,
                'location_id': source.id,
                'location_dest_id': destination.id,
                'lot_id': lot.id if lot else False,
                'company_id': self.env.company.id,
            })
        else:
            for ml in move.move_line_ids:
                ml.qty_done = qty
                if lot:
                    ml.lot_id = lot.id

        move._action_done()

    # -------------------------------
    # START WORKORDER
    # -------------------------------
    def button_start(self, *args, **kwargs):
        res = super().button_start(*args, **kwargs)

        for wo in self:
            workorders = wo.production_id.workorder_ids.sorted('sequence')
            if not workorders:
                continue

            first_wo = workorders[0]

            if wo.id != first_wo.id:
                continue

            source = wo.production_id.location_src_id
            dest = wo.workcenter_id.location_id

            if not source or not dest:
                continue

            for move in wo.production_id.move_raw_ids:

                # 🔥 FORCE RESERVATION
                move._action_assign()

                # CASE 1: with lots
                if move.move_line_ids:
                    for ml in move.move_line_ids:
                        qty = ml.qty_done or ml.product_uom_qty or 1

                        self._move_lot(
                            lot=ml.lot_id,
                            source=source,
                            destination=dest,
                            product=ml.product_id,
                            qty=qty
                        )

                # CASE 2: NO LOTS (fallback)
                else:
                    self._move_lot(
                        lot=False,
                        source=source,
                        destination=dest,
                        product=move.product_id,
                        qty=move.product_uom_qty
                    )

        return res

    # -------------------------------
    # FINISH WORKORDER
    # -------------------------------
    def button_finish(self, *args, **kwargs):
        res = super().button_finish(*args, **kwargs)

        for wo in self:
            workorders = wo.production_id.workorder_ids.sorted('sequence')
            if not workorders:
                continue

            next_wo = False
            for i, w in enumerate(workorders):
                if w.id == wo.id and i + 1 < len(workorders):
                    next_wo = workorders[i + 1]
                    break

            source = wo.workcenter_id.location_id
            dest = next_wo.workcenter_id.location_id if next_wo else wo.production_id.location_dest_id

            if not source or not dest:
                continue

            for move in wo.production_id.move_raw_ids:

                # 🔥 FORCE RESERVATION
                move._action_assign()

                # CASE 1: with lots
                if move.move_line_ids:
                    for ml in move.move_line_ids:
                        qty = ml.qty_done or ml.product_uom_qty or 1

                        self._move_lot(
                            lot=ml.lot_id,
                            source=source,
                            destination=dest,
                            product=ml.product_id,
                            qty=qty
                        )

                # CASE 2: NO LOTS
                else:
                    self._move_lot(
                        lot=False,
                        source=source,
                        destination=dest,
                        product=move.product_id,
                        qty=move.product_uom_qty
                    )

        return res


# -------------------------------
# Quality Check Display
# -------------------------------
class QualityCheck(models.Model):
    _inherit = 'quality.check'
    final_image = fields.Binary("Final Product Image", attachment=True)
    final_image_filename = fields.Char("Image Filename")
    employee_history = fields.Text(
        string="Employee Work History",
        compute="_compute_employee_history",
        store=False
    )
    product_barcode = fields.Char(
        string="Product Barcode",
        related="product_id.barcode",
        store=False
    )

    def _compute_employee_history(self):
        for rec in self:

            # ❗ No workorder → nothing
            if not rec.workorder_id or not rec.workorder_id.workcenter_id:
                rec.employee_history = ""
                continue

            # ✅ Get employees from CURRENT workcenter only
            employees = rec.workorder_id.workcenter_id.employee_ids

            rec.employee_history = ", ".join(employees.mapped('name')) or "No Employee"

    faulty_component_id = fields.Many2many(
        'product.product',
        'quality_check_faulty_product_rel',
        'quality_check_id',
        'product_id',
        string="Faulty Components"
    )
    worksheet_document = fields.Binary(
        related='point_id.worksheet_document',
        string="Worksheet (Image/PDF)",
        readonly=True
    )
    instruction_note = fields.Html(
        related='point_id.note',
        string="Instructions",
        readonly=True
    )
    faulty_lot_id = fields.Many2many(
        'stock.lot',
        'quality_check_faulty_lot_rel',
        'quality_check_id',
        'lot_id',
        string="Component Serial Numbers"
    )
    employee_ids = fields.Many2many(
        'hr.employee',
        string="Allowed Employees",
        compute="_compute_employee_ids",
        store=True
    )
    workorder_id = fields.Many2one('mrp.workorder')
    @api.onchange('faulty_component_id')
    def _onchange_faulty_component(self):
        if self.production_id and self.faulty_component_id:
            # ✅ Get all available stock (only available serials)
            quants = self.env['stock.quant'].search([
                ('product_id', 'in', self.faulty_component_id.ids),
                ('quantity', '>', 0)
            ])

            all_lots = quants.mapped('lot_id')

            # ❌ REMOVE used lots in this MO
            used_lots = self.production_id.move_raw_ids.mapped('move_line_ids.lot_id')

            available_lots = all_lots - used_lots

            return {
                'domain': {
                    'faulty_lot_id': [('id', 'in', available_lots.ids)]
                }
            }

    @api.model
    def create(self, vals):
        record = super().create(vals)

        if record.workorder_id:
            lines = self.env['mrp.workorder.line'].search([
                ('workorder_id', '=', record.workorder_id.id)
            ])

            employees = lines.mapped('employee_ids')

            record.employee_ids = [(6, 0, employees.ids)]

        return record

    @api.depends('workorder_id.workcenter_id.employee_ids')
    def _compute_employee_ids(self):
        for rec in self:
            if rec.workorder_id and rec.workorder_id.workcenter_id:
                rec.employee_ids = rec.workorder_id.workcenter_id.employee_ids
            else:
                rec.employee_ids = [(5, 0, 0)]



    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.quality_state == 'pass' and not rec.final_image:
                raise ValidationError("Please upload final product image before passing.")
        return res
# -------------------------------
# AUTO BARCODE GENERATION
# -------------------------------
class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        # Generate barcode if not provided
        if not vals.get('barcode'):
            vals['barcode'] = self.env['ir.sequence'].next_by_code('product.barcode') or '/'
        return super(ProductProduct, self).create(vals)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        # Backup logic (in case template is created first)
        if not vals.get('barcode'):
            vals['barcode'] = self.env['ir.sequence'].next_by_code('product.barcode') or '/'
        return super(ProductTemplate, self).create(vals)




import base64
import json
import qrcode
from io import BytesIO
import barcode
from barcode.writer import ImageWriter


class StockLot(models.Model):
    _inherit = 'stock.lot'
    production_id = fields.Many2one('mrp.production', string="Production Order")
    # -------------------------------
    # BARCODE
    # -------------------------------
    def get_barcode_image(self):
        self.ensure_one()

        CODE128 = barcode.get_barcode_class('code128')
        code = CODE128(self.name, writer=ImageWriter())

        buffer = BytesIO()
        code.write(buffer)

        return base64.b64encode(buffer.getvalue()).decode()

    def get_qr_code(self):
        self.ensure_one()

        # -------------------------------
        # ✅ URL BASED (PRIMARY)
        # -------------------------------
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url_data = f"{base_url}/traceability/{self.name}"

        try:
            qr = qrcode.make(url_data)

        except Exception:
            # fallback minimal
            minimal_data = {
                "serial_number": self.name
            }
            qr = qrcode.make(json.dumps(minimal_data))

        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        return base64.b64encode(buffer.getvalue()).decode()

class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    location_id = fields.Many2one(
        'stock.location',
        string="Stock Location",
        domain=[('usage', '=', 'internal')],
    )

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    operation_id = fields.Many2one(
        'mrp.routing.workcenter',
        string="Consumed in Operation"
    )

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def log_scan(self, product_name):
        for rec in self:
            rec.message_post(body=f"Scanned & Consumed: {product_name}")




class StockMove(models.Model):
    _inherit = 'stock.move'

    serial_input = fields.Char(string="Scan Serial")

    def action_scan_serial(self):
        for rec in self:

            if not rec.serial_input:
                return

            serial = rec.serial_input.strip()

            if rec.product_id.tracking != 'serial':
                raise ValidationError("Only serial-tracked product allowed.")

            # 🔍 LOT
            lot = self.env['stock.lot'].search([
                ('name', '=', serial),
                ('product_id', '=', rec.product_id.id)
            ], limit=1)

            if not lot:
                raise ValidationError(f"Serial '{serial}' not found.")

            # 🔍 QUANT
            quant = self.env['stock.quant'].search([
                ('product_id', '=', rec.product_id.id),
                ('lot_id', '=', lot.id),
                ('location_id', '=', rec.location_id.id),
                ('quantity', '>', 0),
            ], limit=1)

            if not quant:
                raise ValidationError("Serial not available.")

            # 🚫 duplicate scan
            if lot in rec.move_line_ids.mapped('lot_id'):
                raise ValidationError("Serial already scanned.")

            # 🚨 CHECK LIMIT (IMPORTANT)
            if len(rec.move_line_ids) >= rec.product_uom_qty:
                raise ValidationError("Already scanned required quantity.")

            # 🔥 CREATE NEW LINE (DO NOT DELETE OLD ONES)
            move_line = self.env['stock.move.line'].create({
                'move_id': rec.id,
                'product_id': rec.product_id.id,
                'location_id': rec.location_id.id,
                'location_dest_id': rec.location_dest_id.id,
                'lot_id': lot.id,
                'product_uom_id': rec.product_uom.id,
                'qty_done': 1,
            })

            # 🔥 Assign reservation for this line
            rec._action_assign()

            rec.serial_input = ''