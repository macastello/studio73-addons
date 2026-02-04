# Copyright 2024 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
import logging

import requests

from odoo.exceptions import UserError
from odoo.modules.module import get_module_resource
from odoo.tests.common import TransactionCase

_LOGGER = logging.getLogger(__name__)
LINE_LABEL_LENGTH = 15


class TestEdicomConnector(TransactionCase):
    @classmethod
    def _request_handler(cls, s, r, /, **kw):
        """Don't block external requests."""
        return cls._super_send(s, r, **kw)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._super_send = requests.Session.send

        cls.env.ref("connector_edicom.sale_order_import_edicom")
        cls.import_config = cls.env.ref("connector_edicom.sale_order_import_edicom")

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product A",
                "barcode": "8445333653745",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner 1",
                "edicom_ean13": "8422416000016",
            }
        )
        cabped_file_path = get_module_resource(
            "connector_edicom", "tests", "CABPED.txt"
        )
        lineped_file_path = get_module_resource(
            "connector_edicom", "tests", "LINPED.txt"
        )
        cabped_file = base64.b64encode(open(cabped_file_path, "rb").read())
        linped_file = base64.b64encode(open(lineped_file_path, "rb").read())

        cls.edicom_connector_cabped = cls.env["sale.order.import.edicom"].create(
            {
                "file_ids": [
                    (0, 0, {"filename": "CABPED.txt", "file": cabped_file}),
                    (0, 0, {"filename": "LINPED.txt", "file": linped_file}),
                ]
            }
        )

    def test_01_get_import_config_success(self):
        edicom_connector = self.env["sale.order.import.edicom"].create(
            {
                "file_ids": [
                    (0, 0, {"filename": "test_file.txt", "file": b""}),
                ]
            }
        )
        result = edicom_connector._get_import_config(
            "connector_edicom.sale_order_import_edicom"
        )
        self.assertEqual(
            result.id,
            self.import_config.id,
            "La configuración de importación no se recuperó correctamente.",
        )

    def test_02_get_import_config_failure(self):
        edicom_connector = self.env["sale.order.import.edicom"].create(
            {
                "file_ids": [
                    (0, 0, {"filename": "test_file.txt", "file": b""}),
                ]
            }
        )
        with self.assertRaises(UserError, msg="Import configuration not found."):
            edicom_connector._get_import_config("connector_edicom.non_existent_config")

    def test_03_do_import_cabped(self):
        self.edicom_connector_cabped.action_import()
        sale_orders = self.env["sale.order"].search([("edicom_order_id", "=", "30261")])
        self.assertEqual(len(sale_orders), 1, "No se ha creado el pedido de venta.")
        self.assertEqual(sale_orders[0].partner_id.id, self.partner.id)
        self.assertIsNotNone(
            sale_orders[0].date_order,
            "El campo date_order no se configuró correctamente.",
        )
        sale_order_lines = self.env["sale.order.line"].search(
            [("order_id", "=", sale_orders[0].id)]
        )
        self.assertEqual(
            len(sale_order_lines), 1, "No se ha creado la línea de pedido."
        )
        self.assertEqual(sale_order_lines[0].product_id.id, self.product.id)
        self.assertEqual(sale_order_lines[0].product_uom_qty, 1)
        self.assertEqual(sale_order_lines[0].price_unit, 1)
