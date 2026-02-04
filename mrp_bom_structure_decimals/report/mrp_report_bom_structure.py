# Copyright 2020 Studio73 - Ethan Hildick <ethan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, models
from odoo.tools import float_round


class ReportBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    def _get_precision_digits(self):
        return self.env["decimal.precision"].precision_get("Lista Materiales Costes")

    @api.model
    def _get_component_data(
        self,
        parent_bom,
        parent_product,
        warehouse,
        bom_line,
        line_quantity,
        level,
        index,
        product_info,
        ignore_stock=False,
    ):
        component = super()._get_component_data(
            parent_bom,
            parent_product,
            warehouse,
            bom_line,
            line_quantity,
            level,
            index,
            product_info,
            ignore_stock,
        )
        price = (
            bom_line.product_id.uom_id._compute_price(
                bom_line.product_id.standard_price, bom_line.product_uom_id
            )
            * line_quantity
        )
        precision = self._get_precision_digits()
        component["prod_cost"] = float_round(price, precision_digits=precision)
        component["bom_cost"] = float_round(price, precision_digits=precision)
        component["precision_digits"] = precision
        return component

    def _get_operation_line(self, product, routing, qty, level, index):
        operations = []
        total = 0.0
        operation_index = 0
        company = routing.company_id or self.env.company
        for operation in routing.operation_ids:
            if not product or operation._skip_operation_line(product):
                continue
            operation_cycle = float_round(
                qty / operation.workcenter_id._get_capacity(product),
                precision_rounding=1,
                rounding_method="UP",
            )
            duration_expected = (
                operation_cycle * operation.time_cycle
                + operation.workcenter_id.time_stop
                + operation.workcenter_id.time_start
            )
            total = self._get_operation_cost(duration_expected, operation)
            operations.append(
                {
                    "type": "operation",
                    "index": f"{index}{operation_index}",
                    "level": level or 0,
                    "operation": operation,
                    "link_id": operation.id,
                    "link_model": "mrp.routing.workcenter",
                    "name": operation.name + " - " + operation.workcenter_id.name,
                    "uom_name": "Minutos",
                    "quantity": duration_expected,
                    "bom_cost": self.env.company.currency_id.round(total),
                    "currency_id": company.currency_id.id,
                    "model": "mrp.routing.workcenter",
                }
            )
            operation_index += 1
        return operations

    @api.model
    def _get_bom_data(
        self,
        bom,
        warehouse,
        product=False,
        line_qty=False,
        bom_line=False,
        level=0,
        parent_bom=False,
        parent_product=False,
        index=0,
        product_info=False,
        ignore_stock=False,
    ):
        bom_data = super()._get_bom_data(
            bom,
            warehouse,
            product,
            line_qty,
            bom_line,
            level,
            parent_bom,
            parent_product,
            index,
            product_info,
            ignore_stock,
        )
        bom_data["precision_digits"] = self._get_precision_digits()
        return bom_data
