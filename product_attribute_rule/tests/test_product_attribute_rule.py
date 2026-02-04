# Copyright 2020 Studio73 - Iván Pérez <ivan.perez@studio73.es>
# Copyright 2022 Studio73 - Ioan Galan <ioan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import MissingError
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestAttributeRule(TransactionCase):
    def setUp(self):
        res = super().setUp()

        self.Product = self.env["product.product"]
        self.computer = self.env["product.template"].create({"name": "Super Computer"})
        variant = self.computer.product_variant_id
        self._add_ssd_attribute()
        self._add_ram_attribute()
        self._add_hdd_attribute()
        (self.computer.product_variant_ids - variant).unlink()
        self.attribute_rule = self.env["product.attribute.rule"].create(
            {
                "attribute_x_id": self.ssd_attribute.id,
                "attribute_y_id": self.ram_attribute.id,
                "rule_line_ids": [
                    (
                        0,
                        0,
                        {
                            "value_x": self.ssd_256.id,
                            "value_y": self.ram_16.id,
                            "available": True,
                        },
                    )
                ],
            }
        )

        self.attribute_rule_combine = self.env["product.attribute.rule"].create(
            {
                "action": "combine",
                "attribute_x_id": self.ssd_attribute.id,
                "attribute_y_id": self.hdd_attribute.id,
                "rule_line_ids": [
                    (
                        0,
                        0,
                        {
                            "value_x": self.ssd_512.id,
                            "value_y": self.hdd_2.id,
                            "available": True,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "value_x": self.ssd_256.id,
                            "value_y": self.hdd_2.id,
                            "available": False,
                        },
                    ),
                ],
            }
        )

        self.computer_ssd_256 = self._get_product_template_attribute_value(self.ssd_256)
        self.computer_ssd_512 = self._get_product_template_attribute_value(self.ssd_512)
        self.computer_ram_8 = self._get_product_template_attribute_value(self.ram_8)
        self.computer_ram_16 = self._get_product_template_attribute_value(self.ram_16)
        self.computer_hdd_1 = self._get_product_template_attribute_value(self.hdd_1)
        self.computer_hdd_2 = self._get_product_template_attribute_value(self.hdd_2)
        return res

    def _add_ssd_attribute(self):
        self.ssd_attribute = self.env["product.attribute"].create(
            {"name": "Memory", "sequence": 1, "create_variant": "no_variant"}
        )
        self.ssd_256 = self.env["product.attribute.value"].create(
            {"name": "256 GB", "attribute_id": self.ssd_attribute.id, "sequence": 1}
        )
        self.ssd_512 = self.env["product.attribute.value"].create(
            {"name": "512 GB", "attribute_id": self.ssd_attribute.id, "sequence": 2}
        )
        self.computer_ssd_attribute_lines = self.env[
            "product.template.attribute.line"
        ].create(
            {
                "product_tmpl_id": self.computer.id,
                "attribute_id": self.ssd_attribute.id,
                "value_ids": [(6, 0, [self.ssd_256.id, self.ssd_512.id])],
            }
        )

    def _add_ram_attribute(self):
        self.ram_attribute = self.env["product.attribute"].create(
            {"name": "RAM", "sequence": 2, "create_variant": "no_variant"}
        )
        self.ram_8 = self.env["product.attribute.value"].create(
            {"name": "8 GB", "attribute_id": self.ram_attribute.id, "sequence": 1}
        )
        self.ram_16 = self.env["product.attribute.value"].create(
            {"name": "16 GB", "attribute_id": self.ram_attribute.id, "sequence": 2}
        )
        self.computer_ram_attribute_lines = self.env[
            "product.template.attribute.line"
        ].create(
            {
                "product_tmpl_id": self.computer.id,
                "attribute_id": self.ram_attribute.id,
                "value_ids": [(6, 0, [self.ram_8.id, self.ram_16.id])],
            }
        )

    def _add_hdd_attribute(self):
        self.hdd_attribute = self.env["product.attribute"].create(
            {"name": "HDD", "sequence": 3, "create_variant": "no_variant"}
        )
        self.hdd_1 = self.env["product.attribute.value"].create(
            {"name": "1 To", "attribute_id": self.hdd_attribute.id, "sequence": 1}
        )
        self.hdd_2 = self.env["product.attribute.value"].create(
            {"name": "2 To", "attribute_id": self.hdd_attribute.id, "sequence": 2}
        )
        self.computer_hdd_attribute_lines = self.env[
            "product.template.attribute.line"
        ].create(
            {
                "product_tmpl_id": self.computer.id,
                "attribute_id": self.hdd_attribute.id,
                "value_ids": [(6, 0, [self.hdd_1.id, self.hdd_2.id])],
            }
        )

    def _get_product_template_attribute_value(
        self, product_attribute_value, model=False
    ):
        """
        Return the `product.template.attribute.value` matching
            `product_attribute_value` for self.

        :param: recordset of one product.attribute.value
        :return: recordset of one product.template.attribute.value if found
            else empty
        """
        if not model:
            model = self.computer
        return model.valid_product_template_attribute_line_ids.filtered(
            lambda x: x.attribute_id == product_attribute_value.attribute_id
        ).product_template_value_ids.filtered(
            lambda v: v.product_attribute_value_id == product_attribute_value
        )

    def test_restrict_rule(self):
        self.assertFalse(
            self.computer._is_combination_possible(
                self.computer_ssd_256 + self.computer_ram_16 + self.computer_hdd_1
            )
        )
        self.assertFalse(
            self.Product.create(
                {
                    "product_tmpl_id": self.computer.id,
                    "product_template_attribute_value_ids": [
                        (
                            6,
                            0,
                            [
                                self.computer_ssd_256.id,
                                self.computer_ram_16.id,
                                self.computer_hdd_1.id,
                            ],
                        )
                    ],
                    "active": self.computer.active,
                }
            )
        )
        self.assertTrue(
            self.computer._is_combination_possible(
                self.computer_ssd_256 + self.computer_ram_8 + self.computer_hdd_1
            )
        )
        self.assertTrue(
            self.Product.create(
                {
                    "product_tmpl_id": self.computer.id,
                    "product_template_attribute_value_ids": [
                        (
                            6,
                            0,
                            [
                                self.computer_ssd_256.id,
                                self.computer_ram_8.id,
                                self.computer_hdd_1.id,
                            ],
                        )
                    ],
                    "active": self.computer.active,
                }
            )
        )

    def test_combine_rule(self):
        self.assertFalse(
            self.computer._is_combination_possible(
                self.computer_ssd_256 + self.computer_ram_8 + self.computer_hdd_2
            )
        )
        self.assertFalse(
            self.Product.create(
                {
                    "product_tmpl_id": self.computer.id,
                    "product_template_attribute_value_ids": [
                        (
                            6,
                            0,
                            [
                                self.computer_ssd_256.id,
                                self.computer_ram_8.id,
                                self.computer_hdd_2.id,
                            ],
                        )
                    ],
                    "active": self.computer.active,
                }
            )
        )
        self.assertTrue(
            self.computer._is_combination_possible(
                self.computer_ssd_512 + self.computer_ram_8 + self.computer_hdd_2
            )
        )
        self.assertTrue(
            self.Product.create(
                [
                    {
                        "product_tmpl_id": self.computer.id,
                        "product_template_attribute_value_ids": [
                            (
                                6,
                                0,
                                [
                                    self.computer_ssd_512.id,
                                    self.computer_ram_8.id,
                                    self.computer_hdd_2.id,
                                ],
                            )
                        ],
                        "active": self.computer.active,
                    }
                ]
            )
        )

    def test_archive_variants(self):
        config = self.env["res.config.settings"].create({"archive_variants": True})
        config.execute()
        product_combination = self.env["product.product"].create(
            {
                "product_tmpl_id": self.computer.id,
                "product_template_attribute_value_ids": [
                    (6, 0, [self.computer_ssd_256.id, self.computer_ram_8.id])
                ],
            }
        )
        self.assertTrue(product_combination)
        product_combination._unlink_or_archive()
        self.assertFalse(product_combination.active)

    def test_remove_variants(self):
        config = self.env["res.config.settings"].create({"archive_variants": False})
        config.execute()
        product_combination = self.env["product.product"].create(
            {
                "product_tmpl_id": self.computer.id,
                "product_template_attribute_value_ids": [
                    (6, 0, [self.computer_ssd_256.id, self.computer_ram_8.id])
                ],
            }
        )
        self.assertTrue(product_combination)
        product_combination._unlink_or_archive()
        with self.assertRaises(MissingError, msg="The asset should have been deleted"):
            self.assertFalse(product_combination.active)

    def test_skip_rule_line(self):
        product = self.env["product.template"].create({"name": "Prod Skip Rule 1"})
        attribute_1 = self.env["product.attribute"].create({"name": "Atr Skip Rule 1"})
        attribute_2 = self.env["product.attribute"].create({"name": "Atr Skip Rule 2"})
        attr_value_1 = self.env["product.attribute.value"].create(
            {"name": "Attr Value Skip Rule 1", "attribute_id": attribute_1.id}
        )
        attr_value_2 = self.env["product.attribute.value"].create(
            {"name": "Attr Value Skip Rule 2", "attribute_id": attribute_1.id}
        )
        attr_value_3 = self.env["product.attribute.value"].create(
            {"name": "Attr Value Skip Rule 3", "attribute_id": attribute_2.id}
        )
        attr_value_4 = self.env["product.attribute.value"].create(
            {"name": "Attr Value Skip Rule 4", "attribute_id": attribute_2.id}
        )
        product.write(
            {
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute_1.id,
                            "value_ids": [(6, 0, [attr_value_1.id, attr_value_2.id])],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute_2.id,
                            "value_ids": [(6, 0, [attr_value_3.id])],
                        },
                    ),
                ]
            }
        )
        rule = self.env["product.attribute.rule"].create(
            {
                "action": "combine",
                "attribute_x_id": attribute_1.id,
                "attribute_y_id": attribute_2.id,
                "product_tmpl_ids": [(6, 0, product.ids)],
            }
        )
        with Form(rule) as rule_form:
            rule_form.attribute_x_id = self.env["product.attribute"]
            rule_form.attribute_x_id = attribute_1
            rule_form.save()
        rule_lines = rule.rule_line_ids
        all_values = rule_lines.value_x + rule_lines.value_y
        self.assertTrue(attr_value_4 not in all_values)

    def test_exclusions(self):
        exclusions = self.computer._get_attribute_exclusions()["exclusions"]
        self.assertEqual(len(exclusions[self.computer_ssd_256.id]), 2)
        self.assertEqual(len(exclusions[self.computer_ssd_512.id]), 0)
