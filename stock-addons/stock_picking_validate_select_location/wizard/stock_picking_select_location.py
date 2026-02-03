# Copyright 2022 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPickingSelectLocation(models.TransientModel):
    _name = "stock.picking.select.location"
    _description = "Stock Picking Select Location"
    _inherit = ["barcodes.barcode_events_mixin"]

    parent_location_id = fields.Many2one(
        string="Ubicación padre", comodel_name="stock.location"
    )
    location_id = fields.Many2one(string="Ubicación", comodel_name="stock.location")
    picking_ids = fields.Many2many(string="Albaranes", comodel_name="stock.picking")
    move_line_ids = fields.Many2many(
        string="Movimientos", comodel_name="stock.move.line"
    )

    def assign_location(self):
        if (
            self.picking_ids[0].picking_type_id.dest_location_update_on_validate
            == "always"
        ):
            self.move_line_ids.write({"location_dest_id": self.location_id.id})
        else:
            all_picks = self.picking_ids
            all_picks.write({"forced_dest_location": True})
            picks = self.env["stock.picking"].search(
                [
                    ("id", "in", all_picks.ids),
                    ("state", "not in", ["done", "cancel"]),
                ]
            )
            destinies = picks.move_ids.move_dest_ids.picking_id.batch_id.picking_ids
            all_sibling_pickings = destinies.move_ids.move_orig_ids.picking_id
            all_sibling_pickings.write({"forced_dest_location": True})
            sibling_pickings = (
                self.env["stock.picking"].search(
                    [
                        ("id", "in", all_sibling_pickings.ids),
                        ("state", "not in", ["done", "cancel"]),
                    ]
                )
                | picks
            )
            sibling_pickings.write(
                {"location_dest_id": self.location_id.id, "forced_dest_location": True}
            )
            sibling_pickings.move_line_ids.write(
                {"location_dest_id": self.location_id.id}
            )
        return self.picking_ids.with_context(
            {"skip_check_batch_update_location": True, "skip_backorder": True}
        ).button_validate()

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        location = self.env["stock.location"].search(
            [("barcode", "=", barcode), ("id", "child_of", self.parent_location_id.id)],
            limit=1,
        )
        if location:
            self.location_id = location
