# Copyright 2024 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class AccountMove(models.Model):
    _name = "account.move.line"
    _inherit = ["account.move.line"]

    edicom_dept = fields.Char(
        string="Departamento", readonly=True, states={"draft": [("readonly", False)]}
    )
    edicom_buyer_id = fields.Many2one(
        string="Comprador",
        comodel_name="res.partner",
        states={"draft": [("readonly", False)]},
    )
    edicom_original_order = fields.Char(
        string="Código EDI original", readonly=True, copy=False
    )
