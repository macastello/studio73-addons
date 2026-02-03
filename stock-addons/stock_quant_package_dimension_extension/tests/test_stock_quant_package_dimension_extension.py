# Copyright 2021 Studio73 - Iván Pérez <ivan.perez@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class TeststockQuantPackageDimensionExtension(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_test = cls.env["product.product"].create({"name": "Demo Apple"})
        cls.stock_package_type = cls.env["stock.package.type"]
        cls.stock_package_type.create({"name": "inner"})
        cls.outter_type = cls.env.ref(
            "stock_quant_package_dimension_extension.outer_stock_package_type"
        )
        cls.master_type = cls.env.ref(
            "stock_quant_package_dimension_extension.master_stock_package_type"
        )
        cls.stock_package_type.create({"name": "masterbox"})
        cls.stock_package_type.create({"name": "palet"})
        partner = cls.env["res.partner"].create({"name": "partner 613"})
        cls.purchase = cls.env["purchase.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_test.id,
                            "product_qty": 2,
                            "master_qty": 1,
                        },
                    )
                ],
            }
        )

    def test_01_compute_package_qty(self):
        self.product_test.product_tmpl_id.write(
            {
                "packaging_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "master",
                            "qty": 96,
                            "package_type_id": self.master_type.id,
                            "purchase": True,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "outter",
                            "qty": 72,
                            "package_type_id": self.outter_type.id,
                            "purchase": True,
                        },
                    ),
                ]
            }
        )
        self.product_test.product_tmpl_id._compute_package_qty()
        self.assertEqual(
            self.product_test.product_tmpl_id.package_qty,
            96,
            "La cantidad del empaquetado master es diferente",
        )

    def test_02_ganerate_packagings_by_button(self):
        self.product_test.button_autocreate_packaging()
        standards = self.stock_package_type.search(
            [("allow_auto_create_packaging", "=", True)]
        )
        self.assertEqual(
            len(self.product_test.packaging_ids.ids),
            len(standards),
            "Se deben generar la misma cantidad de paquetes que de estandares creados",
        )

    def test_03_onchange_product_on_purchase(self):
        self.product_test.product_tmpl_id.write(
            {
                "packaging_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "master",
                            "qty": 613,
                            "package_type_id": self.master_type.id,
                            "purchase": True,
                        },
                    ),
                ]
            }
        )
        line = self.purchase.order_line[0]
        self.env.company.force_qty_from_package = True
        line._onchange_product_qty()
        self.assertEqual(line.product_qty, 613, "cantidad incorrecta")

    def test_04_auto_create_packages(self):
        self.product_test.product_tmpl_id.button_autocreate_packaging()
        self.assertEqual(
            len(self.product_test.product_tmpl_id.packaging_ids),
            4,
            "Se deben generar 4 paquetes",
        )
        self.assertTrue(
            all(
                [
                    package.package_type_id.allow_auto_create_packaging
                    for package in self.product_test.product_tmpl_id.packaging_ids
                ]
            ),
            "No se han generado los paquetes correctamente",
        )
