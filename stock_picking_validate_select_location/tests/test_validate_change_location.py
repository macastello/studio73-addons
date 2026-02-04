# Copyright 2022 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import Form, common


class TestPutInPack(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product = cls.env["product.product"].create(
            {"name": "product", "type": "product"}
        )
        wh = cls.env.ref("stock.warehouse0")
        pick_type = wh.int_type_id
        pick_type.dest_location_update_on_validate = "first"
        cls.my_loc = cls.env["stock.location"].create(
            {
                "name": "my_loc",
                "location_id": pick_type.default_location_src_id.id,
                "usage": "internal",
            }
        )
        cls.env["stock.quant"].create(
            {
                "company_id": cls.env.company.id,
                "location_id": wh.lot_stock_id.id,
                "product_id": product.id,
                "quantity": 1,
            }
        )
        pick = Form(cls.env["stock.picking"])
        pick.picking_type_id = pick_type
        with pick.move_ids_without_package.new() as move:
            move.product_id = product
            move.product_uom_qty = 2
        cls.pick = pick.save()
        cls.pick.action_confirm()
        cls.pick.action_assign()
        cls.pick.move_line_ids_without_package[0].write({"qty_done": 1})
        cls.pick.batch_id = cls.env["stock.picking.batch"].create(
            {
                "picking_type_id": pick_type.id,
                "name": "batch",
            }
        )

    def _action_done_check(self):
        res = self.pick.batch_id.action_done()
        self.assertTrue(isinstance(res, dict))
        model = res.get("res_model", False)
        res_id = res.get("res_id", False)
        if model == "stock.backorder.confirmation":
            wiz = (
                self.env["stock.backorder.confirmation"]
                .with_context(res.get("context", {}))
                .create({})
            )
            wiz.backorder_confirmation_line_ids.to_backorder = True
            res = wiz.with_context(button_validate_picking_ids=self.pick.ids).process()
            res_id = res.get("res_id", False)
        wiz = self.env["stock.picking.select.location"].browse(res_id)
        wiz.location_id = self.my_loc
        wiz.assign_location()

    def test_location_assign(self):
        self._action_done_check()
        self.assertEqual(self.pick.location_dest_id, self.my_loc)
        self.assertEqual(
            self.pick.move_line_ids_without_package[0].location_dest_id, self.my_loc
        )

    def test_backorder_location(self):
        self._action_done_check()
        backorder = self.env["stock.picking"].search(
            [("backorder_id", "=", self.pick.id)]
        )
        self.assertTrue(backorder)
        self.assertEqual(backorder.location_dest_id, self.my_loc)
        self.assertTrue(backorder.forced_dest_location)
