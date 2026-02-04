# Copyright 2023 Studio73 - Rafa Ferri <rafa.ferri@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    master_qty = fields.Float("Master", compute="_compute_master")
    outter_qty = fields.Float("Outer", compute="_compute_outter")

    @api.depends("product_id")
    def _compute_master(self):
        master_type = self.env.ref(
            "stock_quant_package_dimension_extension.master_stock_package_type"
        )
        for line in self:
            line.update({"master_qty": line.get_packaging(master_type).qty})

    @api.onchange("product_id", "product_qty", "master_qty")
    def _onchange_product_qty(self):
        if not self.env.company.force_qty_from_package:
            return {}
        for line in self:
            if line.master_qty != 0.0:
                result = line.product_qty % line.master_qty
                if result != 0.0:
                    int_result = line.product_qty // line.master_qty
                    int_result += 1.0
                    line.update({"product_qty": line.master_qty * int_result})

    @api.depends("product_id")
    def _compute_outter(self):
        outter_xmlid = self.env.ref(
            "stock_quant_package_dimension_extension.outer_stock_package_type"
        )
        for line in self:
            line.update({"outter_qty": line.get_packaging(outter_xmlid, False).qty})

    def get_packaging(self, packaging_type, purchase_packaging=True):
        domain = [
            ("product_id", "=", self.product_id.id),
            ("package_type_id", "=", packaging_type.id),
            ("purchase", "=", purchase_packaging),
        ]
        return self.env["product.packaging"].search(domain, limit=1)
