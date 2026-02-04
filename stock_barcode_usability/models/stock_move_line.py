# Copyright 2024 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _apply_putaway_strategy(self):
        excluded_line_ids = self.env["stock.move.line"]
        for move_line in self:
            if (
                move_line.picking_id.picking_type_id.stock_barcode_allow_any_dest_location
                and not move_line.location_dest_id.parent_path.startswith(
                    move_line.move_id.location_dest_id.parent_path
                )
            ):
                excluded_line_ids += move_line
        return super(StockMoveLine, self - excluded_line_ids)._apply_putaway_strategy()

    def _inverse_qty_done(self):
        super()._inverse_qty_done()
        for line in self:
            if (
                line.move_id.picking_type_id.stock_barcode_allow_scan_extra_qty
                or not line.qty_done
            ):
                continue
            if (
                float_compare(
                    line.move_id.product_uom_qty,
                    line.move_id.quantity,
                    precision_rounding=line.move_id.product_uom.rounding,
                )
                < 0
            ):
                raise UserError(
                    _(
                        "No puede añadir más unidades más unidades del producto {} de "
                        "las que hay demandadas".format(line.product_id.display_name)
                    )
                )
