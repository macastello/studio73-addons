# Copyright 2023 Studio73 - Carlos Reyes <carlos@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import Command, fields
from odoo.tests import common


class TestAccountPaymentDateMaturity(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("product.product_product_3")
        cls.partner = cls.env["res.partner"].create(
            {"name": "Set 3 vacas infantil resina"}
        )
        cls.invoice = (
            cls.env["account.move"]
            .with_context(default_move_type="out_invoice")
            .create(
                {
                    "partner_id": cls.partner.id,
                    "invoice_line_ids": [
                        Command.create(
                            {"product_id": cls.product.id, "quantity": 1.0},
                        )
                    ],
                }
            )
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "bank",
                "type": "bank",
                "code": "BNK",
            }
        )

    def test_01_register_payment(self):
        self.invoice.action_post()
        payment_method = self.env.ref("account.account_payment_method_manual_out")
        payment_method_line = self.env["account.payment.method.line"].search(
            [("payment_method_id", "=", payment_method.id)], limit=1
        )
        payment_method_line.journal_id = self.journal
        wiz = (
            self.env["account.payment.register"]
            .with_context(
                active_ids=self.invoice.ids,
                active_model="account.move",
                active_id=self.invoice.id,
            )
            .create(
                {
                    "payment_method_line_id": payment_method_line.id,
                    "amount": self.invoice.amount_total,
                    "date_maturity": fields.date.today(),
                    "communication": self.invoice.name,
                    "journal_id": self.journal.id,
                }
            )
        )
        wiz.action_create_payments()
        payment = self.env["account.payment"].search(
            [("partner_id", "=", self.partner.id)]
        )
        self.assertEqual(
            wiz.date_maturity, payment.date_maturity, "Fecha vencimiento incorrecta"
        )
