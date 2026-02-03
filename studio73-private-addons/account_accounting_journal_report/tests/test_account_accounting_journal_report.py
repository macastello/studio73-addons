# Copyright 2021 Studio73 - Carlos Reyes - <carlos@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from datetime import timedelta

from odoo import fields
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestAccountAccountingJournalReport(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create(
            {"name": "Providersa", "email": "providersa@providersa.com"}
        )
        self.product1 = self.env["product.product"].create(
            {
                "name": "Led lamp",
                "default_code": "LEDLAMP",
                "standard_price": 100,
                "categ_id": self.env.ref("product.product_category_all").id,
            }
        )
        self.journal = self.env["account.journal"].create(
            {"name": "Journal Company 1", "code": "TST", "type": "sale"}
        )
        self.env.ref("base.EUR").active = True
        self.invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "invoice_date": fields.Date.today() - timedelta(days=1),
                "move_type": "out_invoice",
                "journal_id": self.journal.id,
                "currency_id": self.env.ref("base.EUR").id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test_line",
                            "product_id": self.product1.id,
                            "quantity": 1,
                            "price_unit": self.product1.standard_price,
                        },
                    )
                ],
            }
        )

    def test_journal_report(self):
        self.invoice.action_post()
        self.report = self.env["account.accounting_journal"].create(
            {
                "date_from": fields.Date.today() - timedelta(days=1),
                "date_to": fields.Date.today(),
                "company_id": self.env.company.id,
                "level": "4",
            }
        )
        result_pdf = self.report.export_pdf()
        pdf_data = result_pdf.get("data")
        # Hay veces que el debe es primero y hay veces que está segundo
        # Se añaden que el debe puedan ser dos valores, porque puede cargar el coa
        # español o el coa genérico
        self.assertTrue(
            any(
                data.get("debe") in [89.61]
                for data in filter(
                    lambda x: x.get("asiento").startswith("TST"), pdf_data.get("data")
                )
            ),
            "Datos incorrectos",
        )
        self.report.export()
        self.assertNotEqual(self.report.binary_file, False, "csv no creado")
