# Copyright 2023 Studio73 - Ethan Hildick <ethan@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.depends(
        "move_line_ids.result_package_id", "move_line_ids.result_package_id.volume"
    )
    def _compute_volume(self):
        super()._compute_volume()

    def _get_volume_for_qty(self, qty):
        self.ensure_one()
        if self.env.company.package_volume_from_products:
            return super()._get_volume_for_qty(qty)
        volume = 0
        for package in self.move_line_ids.result_package_id:
            volume += package.volume
        return volume
