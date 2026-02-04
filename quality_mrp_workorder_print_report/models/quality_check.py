# Copyright 2024 Studio73 - Alex Garcia - <alex@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models


class QualityCheck(models.Model):
    _inherit = "quality.check"

    def action_print(self):
        report_id = self.point_id.report_id
        report_model = self.point_id.report_model
        copies_number = self.point_id.copies_number
        qty_to_print = self._get_print_qty()
        if report_id:
            if report_model == "product.product":
                self._next()
                return report_id.report_action(
                    ([self.workorder_id.product_id.id] * qty_to_print) * copies_number,
                )
            elif report_model == "stock.lot":
                self._next()
                return report_id.report_action(
                    ([self.workorder_id.finished_lot_id.id] * qty_to_print)
                    * copies_number,
                )
            elif report_model == "mrp.workorder":
                self._next()
                return report_id.report_action(
                    ([self.workorder_id.id] * qty_to_print) * copies_number,
                )
        return super().action_print()
