# Copyright 2023 Studio73 - Roger Amorós <roger@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestCommonPackageDimension(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        meters = cls.env.ref("uom.product_uom_meter")
        config = cls.env["res.config.settings"].create(
            {
                "product_default_length_uom_id": meters.id,
                "package_volume_from_products": False,
            }
        )
        config.execute()
        cls.package_type = cls.env["stock.package.type"].create(
            {
                "name": "test_packaging",
                "height": 1,
                "width": 3,
                "packaging_length": 1,
                "base_weight": 10,
            }
        )
        cls.package_type.length_uom_name = meters.display_name
        cls.package = cls.env["stock.quant.package"].create(
            {"height": 2, "width": 3, "pack_length": 2}
        )
        location_id = cls.env.ref("stock.stock_location_stock").id
        picking_type_id = cls.env.ref("stock.picking_type_internal").id
        product = cls.env["product.product"].create(
            {"name": "test_product", "volume": 10, "weight": 100}
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "location_id": location_id,
                "location_dest_id": location_id,
                "picking_type_id": picking_type_id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "TEST",
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": 1,
                            "location_id": location_id,
                            "location_dest_id": location_id,
                        },
                    )
                ],
            }
        )
