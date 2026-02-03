# Copyright 2024 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.http import request

from odoo.addons.stock_barcode.controllers.stock_barcode import StockBarcodeController


class StockBarcodeLocationProduct(StockBarcodeController):
    def _try_open_product_location(self, barcode):
        result = request.env["product.packaging"].search_read(
            [
                ("barcode", "=", barcode),
            ],
            ["product_id"],
            limit=1,
        )
        if result:
            product = (
                request.env["product.product"].sudo().browse(result[0]["product_id"][0])
            )
            barcode = product.barcode
        return super()._try_open_product_location(barcode)
