# Copyright 2024 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import _, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    def get_related_picking(self):
        def _remove_return_ids(edi_picking, pickings):
            return_sale_ids = [
                p.sale_id.id
                for p in pickings
                if p.state == "done" and p.picking_type_id.code == "incoming"
            ]
            return next(
                (
                    item
                    for item in edi_picking
                    if item.sale_id.id not in return_sale_ids
                ),
                False,
            )

        stock_move_lines = self.env["stock.move.line"].search(
            [
                "|",
                ("result_package_id", "=", self.id),
                ("package_id", "=", self.id),
                ("company_id", "=", self.env.company.id),
            ],
        )
        if not stock_move_lines:
            return False
        pickings = stock_move_lines.mapped("picking_id")
        edi_picking = self.env["stock.picking"].browse()
        for picking in pickings:
            if picking.state == "done" and picking.picking_type_id.code == "outgoing":
                edi_picking |= picking
        if not edi_picking:
            return False
        if len(edi_picking) > 1:
            edi_picking = _remove_return_ids(edi_picking, pickings)
            if not edi_picking:
                self.message_post(
                    body=_(
                        "No hay picking de salida relacionado con este paquete.\n"
                        "Por favor, comprueba que todo esté correcto."
                    )
                )
        return edi_picking
