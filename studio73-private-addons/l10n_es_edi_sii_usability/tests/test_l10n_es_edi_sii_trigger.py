# Copyright 2024 Studio73 - Óscar Seguí <oscar@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestAccountPaymentAdvanced(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_id = cls.env.ref("base.res_partner_12")
        cls.company_id = cls.env.ref("base.main_company")
        cls.company_id.sii_send_mode = "delayed"
        cls.company_id.sii_delay_time = 48.0
        cls.company_id.vat = "ES00000000T"
        cls.test_edi_format = (
            cls.env["account.edi.format"]
            .sudo()
            .create(
                {
                    "name": "test_edi_format",
                    "code": "test_edi_format",
                }
            )
        )
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Test Tax",
                "amount": 21,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "tax_scope": "service",
            }
        )

        cls.product_id = cls.env.ref("product.product_product_4")
        cls.invoice_id = cls.env["account.move"].create(
            {
                "name": "Test account",
                "partner_id": cls.partner_id.id,
                "invoice_date": fields.Date.from_string("2025-06-11"),
                "move_type": "out_invoice",
                "line_ids": [
                    Command.create(
                        {
                            "name": "Test line 1",
                            "product_id": cls.product_id.id,
                            "quantity": 5,
                            "price_unit": cls.product_id.standard_price,
                            "tax_ids": [(6, 0, cls.tax.ids)],
                            "price_subtotal": cls.product_id.standard_price * 5,
                            "price_total": cls.product_id.standard_price * 5,
                        },
                    )
                ],
            }
        )
        cls.invoice_id.journal_id.edi_format_ids |= cls.test_edi_format
        cls.total_to_compare = 3025.0

    def test_confirm_invoice(self):
        self.invoice_id.action_post()
        self.env["account.edi.format"]._l10n_es_edi_sii_post_invoices_cron(
            self.invoice_id
        )
        self.invoice_id.process_sii_cron_triggers()
        self.invoice_id._post_invoice_to_sii()
        self.assertTrue(self.invoice_id.sii_send_date)
        self.assertTrue(self.invoice_id.sii_cron_trigger_ids)

        data = self.test_edi_format._l10n_es_edi_get_invoices_info(self.invoice_id)
        total = data[0].get("FacturaExpedida", {}).get("ImporteTotal", {})
        self.assertEqual(total, self.total_to_compare)
