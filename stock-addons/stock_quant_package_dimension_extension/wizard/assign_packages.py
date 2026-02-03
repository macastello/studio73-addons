# Copyright 2023 Studio73 - Adrian Pasca <adri.pasca@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AssignPackages(models.TransientModel):
    _name = "assign.packages"
    _description = "Asignar paquetes"

    def assign_package(self):
        for package_type in self.package_type:
            for active_id in self.env.context.get("active_ids"):
                if self.env["product.packaging"].search_count(
                    [
                        ("product_id", "=", active_id),
                        ("package_type_id", "=", package_type.id),
                    ]
                ):
                    continue
                self.env["product.packaging"].create(
                    {
                        "name": package_type.name,
                        "package_type_id": package_type.id,
                        "product_id": active_id,
                        "qty": package_type.quantity_by_package,
                    }
                )
        return True

    package_type_ids = fields.Many2many(
        string="Tipo de paquete", required=True, comodel_name="stock.package.type"
    )
