# Copyright 2023 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class TestMoveAutoReserve(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        stock_loc = cls.env.ref("stock.stock_location_stock")
        int_type = cls.env.ref("stock.picking_type_internal")
        int_type.allow_reserve_relocating = True
        cls.shelf_1_loc = cls.env.ref("stock.stock_location_components")
        product = cls.env["product.product"].create(
            {
                "name": "Set 3 vacas infantil resina",
                "type": "product",
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            product, stock_loc, quantity=10
        )
        cls.out_move = cls.env["stock.move"].create(
            {
                "name": product.name,
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": 10,
                "company_id": cls.env.company.id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": stock_loc.id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
            }
        )
        cls.out_move._action_confirm()
        cls.out_move._action_assign()
        cls.int_move = cls.env["stock.move"].create(
            {
                "name": product.name,
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": 10,
                "company_id": cls.env.company.id,
                "picking_type_id": int_type.id,
                "location_id": stock_loc.id,
                "location_dest_id": cls.shelf_1_loc.id,
            }
        )
        cls.env["stock.move.line"].create(
            {
                "move_id": cls.int_move.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "quantity": 10,
                "picked": True,
                "company_id": cls.env.company.id,
                "location_id": stock_loc.id,
                "location_dest_id": cls.shelf_1_loc.id,
            }
        )

    def test_reserve_relocation_01(self):
        self.assertEqual(sum(ml.quantity for ml in self.out_move.move_line_ids), 10)
        self.int_move._action_done()
        self.assertEqual(sum(ml.quantity for ml in self.out_move.move_line_ids), 10)
        self.assertEqual(self.out_move.move_line_ids[0].location_id, self.shelf_1_loc)

    def test_reserve_relocation_02(self):
        # Aquí se comprueba que Odoo no haya podido hacer la reserva de nuevo a otra
        # ubicación.
        sibling_loc = self.env["stock.location"].create(
            {
                "location_id": self.int_move.location_id.location_id.id,
                "name": "Sibling location",
                "usage": "internal",
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            self.int_move.product_id, sibling_loc, quantity=10
        )
        self.int_move._action_done()
        self.assertEqual(sum(ml.quantity for ml in self.out_move.move_line_ids), 10)
        self.assertEqual(self.out_move.move_line_ids[0].location_id, self.shelf_1_loc)
