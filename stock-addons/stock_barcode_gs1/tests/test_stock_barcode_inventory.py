# Copyright 2024 Studio73 - Ioan Galan <ioan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import tagged

from odoo.addons.stock_barcode.controllers.stock_barcode import StockBarcodeController
from odoo.addons.stock_barcode.tests.test_barcode_client_action import (
    TestBarcodeClientAction,
)
from odoo.addons.website.tools import MockRequest


@tagged("post_install", "-at_install")
class TestStockBarcodeInventory(TestBarcodeClientAction):
    def test_inventory_gs1(self):
        self.clean_access_rights()
        grp_pack = self.env.ref("product.group_stock_packaging")
        self.env.user.write({"groups_id": [(4, grp_pack.id, 0)]})
        with MockRequest(self.env):
            data = StockBarcodeController().get_barcode_data("stock.quant", False)[
                "data"
            ]
            self.assertTrue("product.packaging" in data["records"])

    def test_inventory_gs1_lot_date(self):
        lot_name = "333333"
        write_vals = [
            [
                0,
                0,
                {
                    "dummy_id": 1,
                    "inventory_date": "2024-05-22",
                    "inventory_quantity": 20,
                    "inventory_quantity_set": True,
                    "location_id": self.env.ref("stock.stock_location_stock").id,
                    "lot_name": lot_name,
                    "package_id": False,
                    "product_id": self.product1.id,
                    "user_id": 1,
                    "use_date": "2024-07-15 10:00:00",
                },
            ]
        ]
        with MockRequest(self.env):
            StockBarcodeController().save_barcode_data(
                "stock.quant", False, False, write_vals
            )
            lot = self.env["stock.lot"].search([("name", "=", lot_name)])
            self.assertTrue(self.env["stock.lot"].search([("name", "=", "333333")]))
            self.assertEqual(
                lot.use_date.strftime("%Y-%m-%d %H:%M:%S"),
                "2024-07-15 10:00:00",
            )
