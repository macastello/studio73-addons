# Copyright 2023 Studio73 - Rafa Ferri <rafa.ferri@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command, fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestAccountPaymentAdvanced(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_id = cls.env.ref("base.res_partner_12")
        cls.company_id = cls.env.ref("base.main_company")
        cls.product_id = cls.env.ref("product.product_product_4")
        payment_method_line_id = cls.env.ref("account.account_payment_method_manual_in")
        cls.mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test Credit Transfer to Suppliers",
                "company_id": cls.company_id.id,
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
            }
        )
        cls.journal_id = cls.env["account.journal"].create(
            {
                "name": "Test journal",
                "code": "613",
                "type": "general",
                "payment_mode_id": cls.mode.id,
                "company_id": cls.company_id.id,
                "inbound_payment_method_line_ids": [
                    Command.set(payment_method_line_id.ids)
                ],
            }
        )
        cls.invoice_id = cls.env["account.move"].create(
            {
                "name": "Test account",
                "partner_id": cls.partner_id.id,
                "invoice_date": fields.Date.today(),
                "move_type": "out_invoice",
                "line_ids": [
                    Command.create(
                        {
                            "name": "Chubasquero de pez",
                            "product_id": cls.product_id.id,
                            "quantity": 5,
                            "price_unit": cls.product_id.standard_price,
                        },
                    )
                ],
            }
        )
        cls.tax_account_id = cls.env["account.account"].create(
            {
                "name": "Cigala",
                "code": "659",
                "account_type": "equity",
            }
        )
        cls.invoice2_id = cls.env["account.move"].create(
            {
                "name": "Test account",
                "partner_id": cls.partner_id.id,
                "invoice_date": fields.Date.today(),
                "move_type": "out_invoice",
                "payment_mode_id": cls.mode.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "Chubasquero de pez",
                            "product_id": cls.product_id.id,
                            "quantity": 5,
                            "partner_id": cls.partner_id.id,
                            "price_unit": cls.product_id.standard_price,
                        },
                    )
                ],
                "line_ids": [
                    Command.create(
                        {
                            "account_id": cls.tax_account_id.id,
                            "partner_id": cls.partner_id.id,
                            "debit": 100,
                            "reconciled": False,
                        },
                    )
                ],
            }
        )
        cls.entry_invoice_id = cls.env["account.payment.entry"].create(
            {
                "name": "Out invoice entry",
                "amount": 10.0,
                "amount_unreconciled": 10.0,
                "entry_type": "cr",
                "invoice_id": cls.invoice2_id.id,
            }
        )
        cls.entry_refund_id = cls.env["account.payment.entry"].create(
            {
                "name": "Out invoice refund",
                "amount": 5.0,
                "amount_unreconciled": 5.0,
                "entry_type": "dr",
            }
        )
        cls.account_payment_ad = cls.env["account.payment.advanced"].create(
            {
                "name": "Test account payment advanced",
                "partner_id": cls.partner_id.id,
                "date": fields.Date.today(),
                "journal_id": cls.journal_id.id,
                "amount": 10.0,
                "concile_move_line": True,
                "invoice_ids": [Command.set(cls.invoice_id.ids)],
                "entry_invoice_ids": [Command.set(cls.entry_invoice_id.ids)],
                "entry_refund_ids": [Command.set(cls.entry_refund_id.ids)],
            }
        )

    def test_account_payment_advanced_01(self):
        self.assertEqual(
            self.account_payment_ad.invoices_count, 1, "there should be a invoice"
        )
        tax_account_payment_id = self.account_payment_ad._get_default_writeoff_account()
        self.assertEqual(
            tax_account_payment_id, self.tax_account_id.id, "Tax should be the same"
        )
        self.account_payment_ad._onchange_entry_ids()
        self.assertEqual(
            self.account_payment_ad.writeoff_amount, 5.0, "Amount should be 5.0"
        )
        self.account_payment_ad._onchange_amount()
        self.assertTrue(
            self.entry_invoice_id.reconcile,
            "Amount is the same than payment advance amount",
        )
        self.assertFalse(
            self.entry_refund_id.reconcile,
            "Amount is not the same than payment advance amount",
        )
        self.entry_invoice_id.amount_unreconciled = 5.0
        self.entry_refund_id.amount_unreconciled = -10.0
        self.account_payment_ad._onchange_amount()
        self.assertTrue(
            self.entry_refund_id.reconcile,
            "Amount is the same than payment advance amount",
        )
        self.assertFalse(
            self.entry_invoice_id.reconcile,
            "Amount is not the same than payment advance amount",
        )
        self.account_payment_ad._onchange_journal()
        self.assertEqual(
            self.account_payment_ad.payment_mode_id.id,
            self.mode.id,
            "They should be share same payment mode",
        )

    def test_account_payment_advanced_02(self):
        self.partner_id.property_account_receivable_id = self.tax_account_id
        new_entry_cr = self.account_payment_ad._get_entry_vals("entry", "cr")
        self.assertTrue(new_entry_cr)
        new_entry_dr = self.account_payment_ad._get_entry_vals("entry", "dr")
        self.assertTrue(new_entry_dr)
        with self.assertRaises(UserError):
            self.account_payment_ad._get_entry_vals("entry", "Salxixa crua amb oliet")

    def test_account_payment_advanced_03(self):
        vals_list = {
            "partner_id": self.partner_id.id,
            "date": fields.Date.today(),
            "journal_id": self.journal_id.id,
            "payment_difference_handling": "reconcile",
            "amount": 10.0,
            "writeoff_amount": 10.0,
            "writeoff_account_id": self.tax_account_id.id,
            "invoice_ids": [Command.set(self.invoice_id.ids)],
            "entry_invoice_ids": [Command.set(self.entry_invoice_id.ids)],
            "entry_refund_ids": [Command.set(self.entry_refund_id.ids)],
        }
        new_acc_pay_ad = self.account_payment_ad.create(vals_list)
        self.assertEqual(
            "00001",
            new_acc_pay_ad.name,
            "New payment name should be like account_payment_advanced_seq names",
        )
        new_acc_pay_ad.entry_invoice_ids.invoice_id.action_post()
        new_acc_pay_ad.action_post_and_new()
        self.assertEqual(
            new_acc_pay_ad.state, "posted", "Account payment should be posted"
        )
        self.assertEqual(
            len(new_acc_pay_ad.account_payment_ids), 1, "There should be one"
        )
        with self.assertRaises(UserError):
            new_acc_pay_ad.unlink()
        action = new_acc_pay_ad.button_open_invoices()
        self.assertTrue(action.get("res_id", False), "There should be one invoice")
        new_acc_pay_ad.invoice_ids = Command.clear()
        action = new_acc_pay_ad.button_open_invoices()
        self.assertFalse(
            action.get("res_id", False), "There aren't should be one invoice"
        )
        with self.assertRaises(UserError):
            new_acc_pay_ad.action_draft()
        new_acc_pay_ad.action_cancel()
        self.assertEqual(
            new_acc_pay_ad.state, "cancel", "Account payment should be cancel"
        )
        new_acc_pay_ad.action_draft()
        self.assertEqual(
            new_acc_pay_ad.state, "draft", "Account payment should be draft"
        )
