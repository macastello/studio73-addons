# Copyright 2023 Studio73 - Roger Amorós <roger@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    package_volume_from_products = fields.Boolean(
        related="company_id.package_volume_from_products",
        readonly=False,
    )
    force_qty_from_package = fields.Boolean(
        related="company_id.force_qty_from_package",
        readonly=False,
    )
    package_type_id = fields.Many2one(
        comodel_name="stock.package.type",
        string="Tipo de paquete por defecto",
        related="company_id.package_type_id",
        help="El tipo de paquete aquí seleccionado se asignará por defecto"
        " al crear poner mercancía en paquete",
        readonly=False,
    )
