# Copyright 2022 Studio73 - Ethan Hildick <ethan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import Form, common


class TestTrialBalance(common.TransactionCase):
    def _get_trial_wizard(self, level="max"):
        wizard_form = Form(self.env["trial.balance.report.wizard"])
        wizard_form.date_from = "2022-01-01"
        wizard_form.date_to = "2022-01-31"
        wizard_form.level = level
        wizard_form.show_hierarchy = False
        wizard_form.hide_account_at_0 = True
        wizard_form.target_move = "posted"
        return wizard_form.save()

    def test_level_1(self):
        wiz = self._get_trial_wizard("1")
        data = wiz.button_export_pdf()["context"]["report_action"]["data"]
        vals = self.env[
            "report.account_financial_report.trial_balance"
        ]._get_report_values(False, data)["trial_balance"]
        self.assertEqual(len(vals[0]["code"]), 1)

    def test_level_2(self):
        wiz = self._get_trial_wizard("2")
        data = wiz.button_export_pdf()["context"]["report_action"]["data"]
        vals = self.env[
            "report.account_financial_report.trial_balance"
        ]._get_report_values(False, data)["trial_balance"]
        self.assertEqual(len(vals[0]["code"]), 2)

    def test_level_3(self):
        wiz = self._get_trial_wizard("3")
        data = wiz.button_export_pdf()["context"]["report_action"]["data"]
        vals = self.env[
            "report.account_financial_report.trial_balance"
        ]._get_report_values(False, data)["trial_balance"]
        self.assertEqual(len(vals[0]["code"]), 3)

    def test_level_4(self):
        wiz = self._get_trial_wizard("4")
        data = wiz.button_export_pdf()["context"]["report_action"]["data"]
        vals = self.env[
            "report.account_financial_report.trial_balance"
        ]._get_report_values(False, data)["trial_balance"]
        self.assertEqual(len(vals[0]["code"]), 4)

    def test_level_max(self):
        wiz = self._get_trial_wizard("max")
        data = wiz.button_export_pdf()["context"]["report_action"]["data"]
        vals = self.env[
            "report.account_financial_report.trial_balance"
        ]._get_report_values(False, data)["trial_balance"]
        self.assertTrue(len(vals[0]["code"]) > 4)
