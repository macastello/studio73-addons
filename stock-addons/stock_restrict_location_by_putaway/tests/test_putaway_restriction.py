# Copyright 2024 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import Command, exceptions
from odoo.tests import common


class TestPutawayRestriction(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["stock.storage.category"].create(
            {
                "name": "Test Category",
                "max_weight": 1,
            }
        )
        location = cls.env["stock.location"].create(
            {
                "name": "Test Location",
                "location_id": cls.env.ref("stock.stock_location_locations").id,
                "storage_category_id": cls.category.id,
            }
        )
        product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "weight": 2,
                "volume": 2,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            product, cls.env.ref("stock.stock_location_stock"), 1
        )
        ptype = cls.env.ref("stock.picking_type_internal")
        ptype.restrict_location_by_putaway = True
        cls.pick = cls.env["stock.picking"].create(
            {
                "picking_type_id": ptype.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "location_dest_id": location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "Test Move",
                            "product_id": product.id,
                            "product_uom_qty": 1,
                            "location_id": cls.env.ref("stock.stock_location_stock").id,
                            "location_dest_id": location.id,
                        }
                    )
                ],
            }
        )
        cls.pick.action_confirm()

    def test_putaway_restriction(self):
        self.pick.action_assign()
        self.pick.move_ids.picked = True
        with self.assertRaises(exceptions.UserError):
            self.pick.button_validate()
        self.category.max_weight = 9999
        self.pick.button_validate()
        self.assertEqual(self.pick.state, "done")

    def test_max_volume(self):
        self.category.max_weight = 9999
        self.category.max_volume = 1
        self.pick.action_assign()
        self.pick.move_ids.picked = True
        with self.assertRaises(exceptions.UserError):
            self.pick.button_validate()
        self.category.max_volume = 0
        self.pick.button_validate()
        self.assertEqual(self.pick.state, "done")
