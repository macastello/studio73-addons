# Copyright 2024 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase

from odoo.addons.stock_barcode_location_product_info.controllers.main import (
    StockBarcodeLocationProduct,
)
from odoo.addons.website.tools import MockRequest


class TestStockBarcodeLocationProductInfo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Set 3 vacas infantil resina",
                "type": "product",
                "barcode": "1234567890",
            }
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

    def test_barcode_location_product_info(self):
        barcode = "1234567890"
        with MockRequest(self.env):
            action = StockBarcodeLocationProduct()._try_open_product_location(barcode)
        self.assertTrue(action["action"])
        self.stock_location.write({"barcode": "abcdefghij"})
        with MockRequest(self.env):
            action = StockBarcodeLocationProduct().try_open_location("abcdefghij")
        self.assertTrue(action["action"]["context"]["scan_location"])
