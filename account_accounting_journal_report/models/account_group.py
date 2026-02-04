# Copyright 2021 Studio73 - Carlos Reyes - <carlos@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountGroup(models.Model):
    _inherit = "account.group"

    level = fields.Integer(store=True)
