# Copyright 2024 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def get_stock_barcode_data_records(self):
        res = super().get_stock_barcode_data_records()
        res.update({"force_increment": self.env.company.stock_barcode_force_increment})
        return res
