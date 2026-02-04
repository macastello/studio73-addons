# Copyright 2021 Studio73 - Iván Pérez <ivan.perez@studio73.es>
# Copyright 2023 Studio73 - Adrian Pasca <adri.pasca@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    package_qty = fields.Float(
        digits="Product Unit of Measure", compute="_compute_package_qty"
    )

    def _compute_package_qty(self):
        for product in self:
            master_type = self.env.ref(
                "stock_quant_package_dimension_extension.master_stock_package_type"
            )
            qty = sum(
                item.qty
                for item in product.packaging_ids
                if item.package_type_id.id == master_type.id
                and (item.sales or item.purchase)
            )
            product.update({"package_qty": qty})

    def button_autocreate_packaging(self):
        self.ensure_one()
        packaging_types = self.env["stock.package.type"].search(
            [("allow_auto_create_packaging", "=", True)]
        )
        vals_list = []
        if len(self.product_variant_ids) > 1:
            return True
        for pack_type in packaging_types:
            if self.env["product.packaging"].search_count(
                [
                    ("product_id", "=", self.product_variant_id.id),
                    ("package_type_id", "=", pack_type.id),
                    ("sales", "=", False),
                    ("purchase", "=", False),
                ]
            ):
                continue
            vals_list.append(self._get_package_vals(pack_type))
        self.env["product.packaging"].create(vals_list)

    def _get_package_vals(self, package_type):
        self.ensure_one()
        return self.product_variant_id._get_package_vals(package_type)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_package_vals(self, package_type):
        self.ensure_one()
        return {
            "name": package_type.name,
            "product_id": self.id,
            "sales": False,
            "purchase": False,
            "package_type_id": package_type.id,
            "company_id": self.company_id.id,
        }

    def button_autocreate_packaging(self):
        self.ensure_one()
        packaging_types = self.env["stock.package.type"].search(
            [("allow_auto_create_packaging", "=", True)]
        )
        vals_list = []
        for pack_type in packaging_types:
            if self.env["product.packaging"].search_count(
                [
                    ("product_id", "=", self.id),
                    ("package_type_id", "=", pack_type.id),
                    ("sales", "=", False),
                    ("purchase", "=", False),
                ]
            ):
                continue
            vals_list.append(self._get_package_vals(pack_type))
        self.env["product.packaging"].create(vals_list)

    def action_assign_packages(self):
        view_id = self.env.ref(
            "stock_quant_package_dimension_extension.assign_packages_form"
        ).id
        return {
            "name": _("Selecciona el paquete"),
            "type": "ir.actions.act_window",
            "res_model": "assign.packages",
            "view_id": view_id,
            "view_mode": "form",
            "target": "new",
            "context": {"active_ids": self.ids, "active_model": "product.product"},
        }
