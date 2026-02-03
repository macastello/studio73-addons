# Copyright 2022 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import Command, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    forced_dest_location = fields.Boolean(
        string="Ubicación destino forzada", copy=False
    )

    def _pre_action_done_hook(self):
        res = super()._pre_action_done_hook()
        if (
            res
            and isinstance(res, dict)
            or self.picking_type_id.dest_location_update_on_validate == "never"
            or self.env.context.get("skip_check_batch_update_location", False)
        ):
            return res
        if self.picking_type_id.dest_location_update_on_validate == "first" and any(
            p.forced_dest_location for p in self
        ):
            return res
        vals = {
            "parent_location_id": self.picking_type_id.default_location_dest_id.id,
            "picking_ids": [(Command.set(self.ids))],
        }
        if self.picking_type_id.dest_location_update_on_validate == "always":
            lines_todo = self.env["stock.move.line"].search(
                [
                    ("picking_id", "in", self.ids),
                    ("state", "not in", ["cancel", "done"]),
                ]
            )
            if lines_todo:
                vals.update({"move_line_ids": [(Command.set(lines_todo.ids))]})
        wiz = self.env["stock.picking.select.location"].create(vals)
        view_id = self.env.ref(
            "stock_picking_validate_select_location.picking_select_location"
        ).id
        return {
            "name": "Seleccionar ubicación destino",
            "view_mode": "form",
            "res_model": "stock.picking.select.location",
            "view_id": view_id,
            "views": [(view_id, "form")],
            "type": "ir.actions.act_window",
            "res_id": wiz.id,
            "target": "new",
        }

    def copy(self, default=None):
        if not default:
            default = {}
        if (
            "backorder_id" in default
            and self.forced_dest_location
            and self.picking_type_id.dest_location_update_on_validate == "first"
        ):
            default.update(
                {
                    "forced_dest_location": True,
                    "location_dest_id": self.location_dest_id.id,
                }
            )
        return super().copy(default)

    def write(self, vals):
        batch_id = vals.get("batch_id", False)
        if not batch_id:
            return super().write(vals)
        batch = self.env["stock.picking.batch"].browse(batch_id)
        if batch.picking_type_id.dest_location_update_on_validate != "first":
            return super().write(vals)
        other_pick = fields.first(
            batch.picking_ids.filtered_domain([("forced_dest_location", "=", True)])
        )
        other_pick = self.env["stock.picking"].search(
            [
                ("batch_id", "=", batch_id),
                ("forced_dest_location", "=", True),
            ],
            limit=1,
        )
        if other_pick:
            location_id = other_pick.location_dest_id.id
            vals.update({"forced_dest_location": True, "location_dest_id": location_id})
            for move in self.move_ids:
                if move.state in ["done", "cancel"]:
                    continue
                move.write({"location_dest_id": location_id})
                for line in move.move_line_ids:
                    if line.state in ["done", "cancel"]:
                        continue
                    line.write({"location_dest_id": location_id})
        return super().write(vals)
