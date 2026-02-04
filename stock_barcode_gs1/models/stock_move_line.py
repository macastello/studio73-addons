# Copyright 2024 Studio73 - Ioan Galan <ioan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    use_date = fields.Datetime(
        string="Fecha de consumo preferente",
        help="Fecha en la que el lote debe ser consumido",
        copy=False,
    )

    def _prepare_new_lot_vals(self):
        self.ensure_one()
        vals = super()._prepare_new_lot_vals()
        if self.use_date and not vals.get("use_date"):
            vals["use_date"] = self.use_date
        return vals
