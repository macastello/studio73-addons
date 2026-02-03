# Copyright 2017 Studio73 - Abraham Anes <abraham@studio73.es>
# Copyright 2022 Studio73 - Ethan Hildick <ethan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class TrialBalanceReport(models.AbstractModel):
    _inherit = "report.account_financial_report.trial_balance"

    def _get_report_values(self, docids, data):
        vals = super()._get_report_values(docids, data)
        foreign_currency = data["foreign_currency"]
        show_hierarchy = data["show_hierarchy"]
        level = data["level"]
        accounts_data = vals.get("accounts_data")
        total_amount = vals.get("total_amount")
        if not show_hierarchy and level != "max":
            groups_data = {}
            accounts_ids = list(accounts_data.keys())
            accounts = self.env["account.account"].browse(accounts_ids)
            for account in accounts:
                key = account.code[: int(level)]
                account_id = account.id
                name = account.group_id.name if account.group_id else account.name
                default_vals = {
                    "code": key,
                    "id": account_id,
                    "name": name,
                    "type": "account_type",
                    "initial_balance": 0.0,
                    "credit": 0.0,
                    "debit": 0.0,
                    "balance": 0.0,
                    "ending_balance": 0.0,
                }
                if foreign_currency:
                    default_vals.update(
                        {
                            "initial_currency_balance": 0.0,
                            "ending_currency_balance": 0.0,
                        }
                    )
                groups_data.setdefault(key, default_vals)
                groups_data[key]["initial_balance"] += total_amount[account_id][
                    "initial_balance"
                ]
                groups_data[key]["debit"] += total_amount[account_id]["debit"]
                groups_data[key]["credit"] += total_amount[account_id]["credit"]
                groups_data[key]["balance"] += total_amount[account_id]["balance"]
                groups_data[key]["ending_balance"] += total_amount[account_id][
                    "ending_balance"
                ]
                if foreign_currency:
                    groups_data[key]["initial_currency_balance"] += total_amount[
                        account_id
                    ]["initial_currency_balance"]
                    groups_data[key]["ending_currency_balance"] += total_amount[
                        account_id
                    ]["ending_currency_balance"]
            trial_balance = list(groups_data.values())
            trial_balance = sorted(trial_balance, key=lambda k: k["code"])
            vals["trial_balance"] = trial_balance
        return vals
