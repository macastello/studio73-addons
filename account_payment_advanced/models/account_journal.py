# Copyright 2018-2019 Studio73 - Abraham Anes <abraham@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    for_customer_payments = fields.Boolean(string="Mostrar en pagos a clientes")
    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        string="Modo de pago por defecto en pagos a clientes",
        help="Modo de pago que se establecerá por defecto al crear un nuevo pago de "
        "cliente",
    )
    is_defaulting_debtor_journal = fields.Boolean(string="Diario de morosos")
    credit_impairment_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Cuenta de pérdidas por deterioro de créditos",
    )
    debt_provision_account_id = fields.Many2one(
        comodel_name="account.account", string="Cuenta de provisión de insolvencias"
    )
