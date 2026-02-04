# Copyright 2023 Studio73 - Roger Amorós <roger@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    package_volume_from_products = fields.Boolean(
        string="Calcular dimensiones en base a los productos"
    )
    force_qty_from_package = fields.Boolean(string="Forzar cantidad según el paquete")
    package_type_id = fields.Many2one(
        comodel_name="stock.package.type", string="Tipo de paquete por defecto"
    )
