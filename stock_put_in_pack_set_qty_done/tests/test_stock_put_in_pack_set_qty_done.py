# Copyright 2024 Studio73 - Roger Amorós <roger@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import Command, exceptions
from odoo.tests import common


class TestStockPutInPackSetQtyDone(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_type = cls.env["stock.picking.type"].search(
            [("code", "=", "incoming")], limit=1
        )
        cls.picking_type.write({"show_reserved": True})
        cls.product = cls.env["product.product"].create(
            {"name": "product", "type": "product"}
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.env["res.partner"]
                .create({"name": "test_partner"})
                .id,
                "picking_type_id": cls.picking_type.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "test_move",
                            "product_id": cls.product.id,
                            "product_uom_qty": 10,
                            "location_id": cls.env.ref(
                                "stock.stock_location_suppliers"
                            ).id,
                            "location_dest_id": cls.env.ref(
                                "stock.stock_location_stock"
                            ).id,
                        }
                    )
                ],
            }
        )
        cls.picking.action_confirm()
        cls.picking.action_assign()

    def test_assign_qty_at_put_in_pack(self):
        self.picking_type.assign_qty_at_put_in_pack = True
        self.picking.action_put_in_pack()
        self.assertEqual(self.picking.move_line_ids.quantity, 10)
        self.assertTrue(self.picking.move_line_ids.result_package_id)

    def test_not_assign_qty_at_put_in_pack(self):
        self.picking_type.assign_qty_at_put_in_pack = False
        with self.assertRaises(exceptions.UserError):
            self.picking.action_put_in_pack()
