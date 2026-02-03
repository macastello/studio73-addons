# Copyright 2021 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models
from odoo.tools import float_compare


class ChooseDeliveryPackage(models.TransientModel):
    _inherit = "choose.delivery.package"

    height = fields.Integer(string="Altura")
    width = fields.Integer(string="Ancho")
    pack_length = fields.Integer(string="Largo")
    volume = fields.Float(string="Volumen")
    packaging_weight = fields.Float(
        string="Peso del empaquetado", related="delivery_package_type_id.base_weight"
    )
    length_uom_name = fields.Char("Unidad de longitud")

    @api.model
    def default_get(self, default_fields):
        defaults = super().default_get(default_fields)
        length_uom = self.env[
            "product.template"
        ]._get_length_uom_id_from_ir_config_parameter()
        defaults["length_uom_name"] = length_uom.name
        delivery_package_type_id = defaults.get("delivery_package_type_id")
        if (
            "delivery_package_type_id" not in defaults
            and self.env.company.package_type_id
        ):
            defaults["delivery_package_type_id"] = self.env.company.package_type_id
            delivery_package_type_id = self.env.company.package_type_id
        if self.env.company.package_volume_from_products:
            picking_id = defaults.get("picking_id")
            if picking_id:
                move_lines_ids = self.env["stock.move.line"].search(
                    [
                        ("picking_id", "=", picking_id),
                        ("quantity", "!=", 0),
                        ("result_package_id", "=", False),
                    ]
                )
                height = 0
                width = 0
                pack_length = 0
                for line in move_lines_ids:
                    width += line.product_id.dimensional_uom_id._compute_quantity(
                        line.product_id.product_width, to_unit=length_uom
                    )
                    height += line.product_id.dimensional_uom_id._compute_quantity(
                        line.product_id.product_height, to_unit=length_uom
                    )
                    pack_length += line.product_id.dimensional_uom_id._compute_quantity(
                        line.product_id.product_length, to_unit=length_uom
                    )
                defaults.update(
                    {
                        "height": height,
                        "width": width,
                        "pack_length": pack_length,
                    }
                )
        elif delivery_package_type_id:
            defaults.update(
                {
                    "height": delivery_package_type_id.height,
                    "width": delivery_package_type_id.width,
                    "pack_length": delivery_package_type_id.packaging_length,
                }
            )
        return defaults

    def action_put_in_pack(self):
        custom_package_dimensions = {
            "volume": self.volume,
            "height": self.height,
            "width": self.width,
            "pack_length": self.pack_length,
        }
        ctx = self.env.context.copy()
        ctx.update(
            {
                "custom_package_dimensions": custom_package_dimensions,
                "update_package_name_by_sequence": True,
            }
        )
        return super(ChooseDeliveryPackage, self.with_context(ctx)).action_put_in_pack()

    def _recompute_volume(self):
        default_length_uom = self.env[
            "product.template"
        ]._get_length_uom_id_from_ir_config_parameter()
        default_volume_uom = self.env[
            "product.template"
        ]._get_volume_uom_id_from_ir_config_parameter()
        move_lines_ids = self.env["stock.move.line"].search(
            [
                ("picking_id", "=", self.picking_id.id),
                ("quantity", "!=", 0),
                ("result_package_id", "=", False),
            ]
        )
        volume = 0
        for line in move_lines_ids:
            volume += line.product_id.volume * line.quantity
        height = self.height or self.delivery_package_type_id.height
        width = self.width or self.delivery_package_type_id.width
        pack_length = self.pack_length or self.delivery_package_type_id.packaging_length
        height_uom = width_uom = length_uom = default_length_uom
        volume = self.delivery_package_type_id.calculate_volume_multi_uom(
            pack_length=pack_length,
            height=height,
            width=width,
            length_uom_id=length_uom,
            height_uom_id=height_uom,
            width_uom_id=width_uom,
            volume_uom_id=default_volume_uom,
        )
        self.update({"volume": volume})

    @api.onchange("height", "width", "pack_length")
    def _onchange_dimensions_compute_volume(self):
        self._recompute_volume()

    @api.onchange("delivery_package_type_id")
    def _onchange_packaging_weight_set_shipping_weight(self):
        if self.env.company.package_volume_from_products:
            return {}
        default_weight_uom = self.env[
            "product.template"
        ]._get_weight_uom_id_from_ir_config_parameter()
        move_line_ids = self.picking_id.move_line_ids.filtered(
            lambda m: float_compare(
                m.quantity, 0.0, precision_rounding=m.product_uom_id.rounding
            )
            > 0
            and not m.result_package_id
        )
        total_weight = 0.0
        for ml in move_line_ids:
            qty = ml.product_uom_id._compute_quantity(ml.quantity, ml.product_id.uom_id)
            total_weight += qty * ml.product_id.weight_uom_id._compute_quantity(
                ml.product_id.weight, default_weight_uom
            )
        self.shipping_weight = total_weight + self.packaging_weight
        return self._onchange_package_type_weight()

    @api.onchange("delivery_package_type_id")
    def _onchange_delivery_package_type_id_set_dimensions(self):
        if (
            self.delivery_package_type_id
            and not self.env.company.package_volume_from_products
        ):
            self.update(
                {
                    "height": self.delivery_package_type_id.height,
                    "width": self.delivery_package_type_id.width,
                    "pack_length": self.delivery_package_type_id.packaging_length,
                }
            )
