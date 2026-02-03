# Copyright 2018 Consultoría Informática Studio73 SL (contacto@studio73.es)
#        Abraham Anes <abraham@studio73.es>
# Copyright 2022 Studio73 - Ethan Hildick <ethan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class TrialBalanceReportWizard(models.TransientModel):
    _inherit = "trial.balance.report.wizard"

    level = fields.Selection(
        selection=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("max", "Max")],
        string="Level",
        required=True,
        default="max",
    )
    print_date = fields.Datetime(
        string="Fecha de impresión", default=fields.Datetime.now, required=True
    )

    @api.onchange("level")
    def onchange_level(self):
        if self.level in ["1", "2", "3", "4"]:
            self.show_hierarchy = False

    def _prepare_report_trial_balance(self):
        self.ensure_one()
        res = super()._prepare_report_trial_balance()
        res.update({"level": self.level, "print_date": self.print_date})
        return res
