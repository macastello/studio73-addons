# Copyright 2021 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).+

from odoo.tests.common import TransactionCase


class TestPackageSequence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        sequence = cls.env["ir.sequence"].create(
            {"name": "test_sequence", "prefix": "text_pack_seq", "padding": 1}
        )
        cls.default_packaging = cls.env["stock.package.type"].create(
            {"name": "test_packaging", "package_sequence_id": sequence.id}
        )
        cls.env.company.package_type_id = cls.default_packaging

    def test_package_sequence(self):
        package = self.env["stock.quant.package"].create({"name": "test_package"})
        package.with_context(update_package_name_by_sequence=True).write(
            {"package_type_id": self.default_packaging.id}
        )
        self.assertTrue(
            package.name.startswith("text_pack_seq"),
            "Error, no se ha actualizado correctamente el nombre del nuevo paquete "
            "a partir de la secuencia",
        )
