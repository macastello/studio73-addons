# Copyright 2021 Ferran Mora <ferran@studio73.es>
# Copyright 2022 Studio73 - Ethan Hildick <ethan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    volume = fields.Float(
        string="Volume",
        help="The volume of the package",
        compute="_compute_volume",
        store=True,
        digits=(16, 4),
    )

    @api.depends("height", "pack_length", "width", "package_type_id")
    def _compute_volume(self):
        for package in self:
            pack = package.package_type_id
            if package.package_type_id:
                height_uom = width_uom = length_uom = self.env["uom.uom"].search(
                    [("name", "=", pack.length_uom_name)]
                )
                if package.height > 0:
                    height = package.height
                    height_uom = package.length_uom_id
                else:
                    height = pack.height
                if package.width > 0:
                    width = package.width
                    width_uom = package.length_uom_id
                else:
                    width = pack.width
                if package.pack_length > 0:
                    pack_length = package.pack_length
                    length_uom = package.length_uom_id
                else:
                    pack_length = pack.packaging_length
            else:
                length_uom = height_uom = width_uom = package.length_uom_id
                pack_length = package.pack_length
                width = package.width
                height = package.height
            volume = pack.calculate_volume_multi_uom(
                pack_length,
                height,
                width,
                length_uom,
                height_uom,
                width_uom,
                package.volume_uom_id,
            )
            if not volume:
                for quant in package.quant_ids:
                    volume += quant.product_id.volume * quant.quantity
            package.volume = volume

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        to_update = {}
        pack = self.env["stock.package.type"]
        if (
            self.env.company.package_type_id
            and "package_type_id" not in defaults
            and not self.env.context.get("update_package_name_by_sequence", False)
        ):
            to_update["package_type_id"] = self.env.company.package_type_id.id
            pack = self.env.company.package_type_id
        if not pack and "package_type_id" in defaults:
            pack = self.env["stock.package.type"].browse(defaults["package_type_id"])
        if pack and pack.package_sequence_id:
            to_update["name"] = pack.package_sequence_id.next_by_id()
        defaults.update(to_update)
        return defaults

    def write(self, vals):
        if vals.get("package_type_id", False) and self.env.context.get(
            "update_package_name_by_sequence", False
        ):
            pack = self.env["stock.package.type"].browse(vals["package_type_id"])
            if pack.package_sequence_id:
                vals.update({"name": pack.package_sequence_id.next_by_id()})
        return super().write(vals)
