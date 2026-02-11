# Copyright 2023 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import Command, models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    # flake8: noqa: C901
    def _action_done(self, cancel_backorder=False):
        reserved = {}
        for move in self:
            pytpe = move.picking_type_id or move.picking_id.picking_type_id
            if not pytpe.allow_reserve_relocating:
                continue
            for line in move.move_line_ids:
                line_key = (
                    line.product_id,
                    line.location_id,
                    line.lot_id,
                    line.package_id,
                    line.owner_id,
                )
                av_qty = self.env["stock.quant"]._get_available_quantity(
                    line_key[0],
                    line_key[1],
                    lot_id=line_key[2],
                    package_id=line_key[3],
                    owner_id=line_key[4],
                    strict=True,
                )
                if (
                    float_compare(
                        av_qty,
                        line.quantity,
                        precision_rounding=line.product_id.uom_id.rounding,
                    )
                    >= 0
                ):
                    continue
                other_line = self.env["stock.move.line"].search(
                    [
                        ("product_id", "=", line_key[0].id),
                        ("location_id", "=", line_key[1].id),
                        ("lot_id", "=", line_key[2].id),
                        ("package_id", "=", line_key[3].id),
                        ("owner_id", "=", line_key[4].id),
                        ("state", "in", ["partially_available", "assigned"]),
                        ("move_id", "not in", self.ids),
                    ]
                )
                line_dict = {}
                missing_qty = line.quantity - av_qty
                lines_to_unlink = self.env["stock.move.line"]
                for sml in other_line:
                    line_dict.setdefault(sml.move_id, 0)
                    line_dict[sml.move_id] += sml.quantity
                    if (
                        float_compare(
                            missing_qty,
                            sml.quantity,
                            precision_rounding=line.product_id.uom_id.rounding,
                        )
                        < 0
                    ):
                        qty_to_unreseve = missing_qty
                        sml.quantity -= qty_to_unreseve
                    else:
                        qty_to_unreseve = sml.quantity
                        lines_to_unlink |= sml
                    missing_qty -= qty_to_unreseve
                    if missing_qty <= 0:
                        break
                if lines_to_unlink:
                    lines_to_unlink.unlink()
                if line_dict:
                    reserved[line_key] = line_dict
        done_moves = super()._action_done(cancel_backorder=cancel_backorder)
        for line in done_moves.move_line_ids:
            line_key = (
                line.product_id,
                line.location_id,
                line.lot_id,
                line.package_id,
                line.owner_id,
            )
            prev_reserve = reserved.get(line_key, False)
            if not prev_reserve:
                continue
            for move, reserved_qty in prev_reserve.items():
                if not line.location_dest_id.parent_path.startswith(
                    move.location_id.parent_path
                ):
                    continue
                reserved_lines = self.env["stock.move.line"].search(
                    [
                        ("product_id", "=", line_key[0].id),
                        ("location_id", "=", line_key[1].id),
                        ("lot_id", "=", line_key[2].id),
                        ("package_id", "=", line_key[3].id),
                        ("owner_id", "=", line_key[4].id),
                        ("state", "in", ["partially_available", "assigned"]),
                        ("move_id", "=", move.id),
                    ]
                )
                current_reserve = sum(ml.quantity for ml in reserved_lines)
                if current_reserve < reserved_qty:
                    has_orig = False
                    if move.procure_method == "make_to_order" and move.move_orig_ids:
                        has_orig = True
                        move.procure_method = "make_to_stock"
                    diff = reserved_qty - current_reserve
                    move._update_reserved_quantity(
                        diff,
                        line.location_dest_id,
                        lot_id=line_key[2],
                        package_id=line.result_package_id,
                        owner_id=line.owner_id,
                        strict=True,
                    )
                    if (
                        sum(ml.quantity for ml in move.move_line_ids)
                        == move.product_uom_qty
                    ):
                        move_vals = {"state": "assigned"}
                    else:
                        move_vals = {"state": "partially_available"}
                    if has_orig:
                        move_vals.update(
                            {
                                "procure_method": "make_to_order",
                                "move_orig_ids": [Command.link(line.move_id.id)],
                            }
                        )
                    move.write(move_vals)
        return done_moves
