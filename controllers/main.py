from odoo import http
from odoo.http import request


class PortalTask(http.Controller):

    @http.route(['/my/task/reset/<int:task_id>'], type='http', auth="user", website=True)
    def reset_task(self, task_id, **kw):

        task = request.env['employee.work.task'].sudo().browse(task_id)

        if task:
            task.action_reset_to_draft()

        return request.redirect('/my/tasks')


class TraceabilityController(http.Controller):

    @http.route('/traceability/<string:serial>', type='http', auth='public', website=True)
    def traceability_page(self, serial=None, **kwargs):

        # -------------------------------
        # ✅ USER TYPE CHECK
        # -------------------------------
        is_internal = request.env.user.has_group('base.group_user')

        # -------------------------------
        # ✅ GET LOT
        # -------------------------------
        lot = request.env['stock.lot'].sudo().search([
            ('name', '=', serial)
        ], limit=1)

        if not lot:
            return "Invalid Serial Number"

        # -------------------------------
        # 🌐 EXTERNAL USER (LIMITED DATA)
        # -------------------------------
        if not is_internal:
            values = {
                "product": lot.product_id.name,
                "serial": lot.name,
                "sales_price": round(lot.product_id.list_price or 0, 2),
                "is_internal": False
            }

            return request.render('employee_work_tracker.traceability_template', values)

        # -------------------------------
        # 🔒 INTERNAL USER (FULL DATA)
        # -------------------------------

        move_line = request.env['stock.move.line'].sudo().search([
            ('lot_id', '=', lot.id)
        ], order="id desc", limit=1)

        production = move_line.move_id.production_id if move_line and move_line.move_id else False

        components = []

        if production:
            for move in production.move_raw_ids:

                lots = move.move_line_ids.mapped('lot_id')

                # -------------------------------
                # Vendor
                # -------------------------------
                vendor = ""
                if move.purchase_line_id:
                    vendor = move.purchase_line_id.order_id.partner_id.name
                elif move.product_id.seller_ids:
                    vendor = move.product_id.seller_ids[0].partner_id.name

                # -------------------------------
                # Purchase Date
                # -------------------------------
                purchase_date = ""

                if move.purchase_line_id:
                    purchase_date = move.purchase_line_id.order_id.date_order

                elif move.product_id.tracking == 'serial':
                    for lot_id in lots:
                        incoming_move_line = request.env['stock.move.line'].sudo().search([
                            ('lot_id', '=', lot_id.id),
                            ('move_id.picking_id.picking_type_id.code', '=', 'incoming')
                        ], order="id desc", limit=1)

                        if incoming_move_line and incoming_move_line.move_id.purchase_line_id:
                            purchase_date = incoming_move_line.move_id.purchase_line_id.order_id.date_order
                            break
                else:
                    incoming_move = request.env['stock.move'].sudo().search([
                        ('product_id', '=', move.product_id.id),
                        ('picking_id.picking_type_id.code', '=', 'incoming'),
                        ('purchase_line_id', '!=', False)
                    ], order="date desc", limit=1)

                    if incoming_move:
                        purchase_date = incoming_move.purchase_line_id.order_id.date_order

                if not purchase_date:
                    purchase_date = move.date

                base_cost = move.product_id.standard_price or 0
                sales_price = move.product_id.list_price or 0

                # SERIAL
                if move.product_id.tracking == 'serial':
                    for lot_id in lots:
                        components.append({
                            "name": move.product_id.name,
                            "serial": lot_id.name,
                            "vendor": vendor,
                            "purchase_date": purchase_date,
                            "cost": round(base_cost, 2),
                            "sales_price": round(sales_price, 2),
                        })

                # NON SERIAL
                else:
                    components.append({
                        "name": move.product_id.name,
                        "serial": "nil",
                        "vendor": vendor,
                        "purchase_date": purchase_date,
                        "cost": round(base_cost, 2),
                        "sales_price": round(sales_price, 2),
                    })

        # -------------------------------
        # FINAL VALUES (INTERNAL)
        # -------------------------------
        values = {
            "product": lot.product_id.name,
            "serial": lot.name,
            "manufactured_date": production.date_start if production else "",
            "cost": round(lot.product_id.standard_price or 0, 2),
            "sales_price": round(lot.product_id.list_price or 0, 2),
            "components": components,
            "is_internal": True
        }

        return request.render('employee_work_tracker.traceability_template', values)
