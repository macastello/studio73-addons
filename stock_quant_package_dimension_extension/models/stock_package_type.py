# Copyright 2023 Studio73 - Roger Amorós <roger@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPackageType(models.Model):
    _inherit = "stock.package.type"

    allow_auto_create_packaging = fields.Boolean(
        "Permitir generar paquete automáticamente",
        help="Al marcar este campo se permite crear automáticamente empaquetados de "
        "este tipo mediante el botón de la ficha del producto 'Crear empaquetados "
        "automaticamente'",
    )
    package_sequence_id = fields.Many2one(
        string="Secuencia de paquetes",
        comodel_name="ir.sequence",
        help="Si se establece una secuencia aquí, está será la que se use para el "
        "nombre de los paquetes que se creen con este tipo",
    )
    quantity_by_package = fields.Float(string="Cantidad por paquete")

    def calculate_volume_multi_uom(
        self,
        pack_length,
        height,
        width,
        length_uom_id,
        height_uom_id,
        width_uom_id,
        volume_uom_id,
    ):
        volume_m3 = 0
        if (
            pack_length
            and height
            and width
            and length_uom_id
            and height_uom_id
            and width_uom_id
        ):
            uom_meters = self.env.ref("uom.product_uom_meter")
            length_m = length_uom_id._compute_quantity(
                qty=pack_length,
                to_unit=uom_meters,
                round=False,
            )
            height_m = height_uom_id._compute_quantity(
                qty=height,
                to_unit=uom_meters,
                round=False,
            )
            width_m = width_uom_id._compute_quantity(
                qty=width,
                to_unit=uom_meters,
                round=False,
            )
            volume_m3 = length_m * height_m * width_m
        return self.env.ref("uom.product_uom_cubic_meter")._compute_quantity(
            qty=volume_m3,
            to_unit=volume_uom_id,
            round=False,
        )
