# Copyright 2021 Studio73 - Ioan Galan <ioan@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from collections import OrderedDict

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    report_grouped_by_picking = fields.Boolean(
        "¿Impresión agrupada por albaranes?", default=True, copy=False, tracking=True
    )

    def lines_grouped_by_picking(self):
        if self.report_grouped_by_picking:
            res = super().lines_grouped_by_picking()
            for index, line in enumerate(res):
                picking = line.get("picking", self.env["stock.picking"])
                if picking and picking.hide_picking_in_report:
                    del res[index]
            return res
        lines_dict = OrderedDict()
        for line in self.invoice_line_ids:
            lines_dict[line] = line.quantity
        no_picking = [
            {"picking": False, "line": key, "quantity": value}
            for key, value in lines_dict.items()
        ]
        return self._sort_grouped_lines(no_picking)

    def _sort_grouped_lines(self, lines_dic):
        if self.report_grouped_by_picking:
            return super()._sort_grouped_lines(lines_dic)
        return sorted(lines_dic, key=lambda x: (x["line"].sequence))
