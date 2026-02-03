# Copyright 2021 Studio73 - Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _put_in_pack(self, move_line_ids):
        package = super()._put_in_pack(move_line_ids)
        custom_dimensions = self.env.context.get("custom_package_dimensions", False)
        if package and custom_dimensions:
            volume = custom_dimensions.pop("volume", None)
            package.write(custom_dimensions)
            if volume:
                # Write por separado para machacar el valor del compute
                package.volume = volume
        return package

    def _set_delivery_package_type(self, batch_pack=False):
        self.ensure_one()
        if self.picking_type_id.hide_delivery_package_wizard:
            return {}
        return super()._set_delivery_package_type(batch_pack=batch_pack)

    @api.depends(
        "move_line_ids.result_package_id", "move_line_ids.result_package_id.volume"
    )
    def _compute_volume(self):
        if self.env.company.package_volume_from_products:
            super()._compute_volume()
        else:
            for picking in self:
                volume = 0
                for package in picking.move_line_ids.result_package_id:
                    volume += package.volume
                picking.volume = volume
