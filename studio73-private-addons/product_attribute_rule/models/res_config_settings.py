# Copyright 2020 Studio73 - Ethan Hildick <ethan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    archive_variants = fields.Boolean(
        string="Archivar variantes",
        config_parameter="product_attribute_rule.archive_variants",
        help="Archivar variantes en lugar de borrarlas cuando"
        "se modifica los atributos de la plantilla de producto"
        "y se recalculan las variantes",
    )
