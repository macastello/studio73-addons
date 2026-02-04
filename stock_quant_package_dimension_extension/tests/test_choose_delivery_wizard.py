# Copyright 2023 Studio73 - Roger Amorós <roger@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import TestCommonPackageDimension


class TestChooseDeliveryPackage(TestCommonPackageDimension):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking.action_confirm()

    def check_package_and_picking_volume(self, package_volume=0, picking_volume=0):
        if not picking_volume:
            picking_volume = package_volume
        package = self.picking.move_line_ids.result_package_id
        self.assertTrue(package)
        self.assertEqual(package.volume, package_volume)
        self.picking._compute_volume()
        self.assertEqual(self.picking.volume, picking_volume)

    def test_choose_delivery_package_01(self):
        wizard = self.env["choose.delivery.package"].create(
            {
                "picking_id": self.picking.id,
                "delivery_package_type_id": self.package_type.id,
            }
        )
        wizard._onchange_delivery_package_type_id_set_dimensions()
        wizard._onchange_packaging_weight_set_shipping_weight()
        wizard._recompute_volume()
        self.assertEqual(wizard.shipping_weight, 110)
        self.assertEqual(wizard.packaging_weight, 10)
        self.assertEqual(wizard.height, 1)
        self.assertEqual(wizard.width, 3)
        self.assertEqual(wizard.pack_length, 1)
        self.assertEqual(wizard.volume, 3)
        wizard.action_put_in_pack()
        self.check_package_and_picking_volume(3)

    def test_choose_delivery_package_02(self):
        wizard = self.env["choose.delivery.package"].create(
            {
                "picking_id": self.picking.id,
                "delivery_package_type_id": self.package_type.id,
                "height": 2,
                "width": 2,
                "pack_length": 2,
            }
        )
        wizard._recompute_volume()
        self.assertEqual(wizard.volume, 8)
        wizard.action_put_in_pack()
        self.check_package_and_picking_volume(8)

    def test_choose_delivery_package_03(self):
        wizard = self.env["choose.delivery.package"].create(
            {"picking_id": self.picking.id, "height": 2, "width": 2, "pack_length": 1}
        )
        wizard._recompute_volume()
        self.assertEqual(wizard.volume, 4)
        wizard.action_put_in_pack()
        self.check_package_and_picking_volume(4)

    def test_choose_delivery_package_04(self):
        config = self.env["res.config.settings"].create(
            {"package_volume_from_products": True}
        )
        config.execute()
        wizard = self.env["choose.delivery.package"].create(
            {"picking_id": self.picking.id}
        )
        wizard._recompute_volume()
        self.assertEqual(wizard.volume, 0)
        wizard.action_put_in_pack()
