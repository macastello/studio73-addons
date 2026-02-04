# Copyright 2024 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from collections import defaultdict

from odoo import models
from odoo.tools import float_compare, float_is_zero


class StockLocation(models.Model):
    _inherit = "stock.location"

    def _storage_category_reason(
        self, product, quantity=0, package=None, location_qty=0
    ):
        # C&P de odoo _check_can_be_used de stock.location para devolver el motivo de
        # fallo en cada caso
        self.ensure_one()
        if self.storage_category_id:
            forecast_weight = self._get_weight(
                self.env.context.get("exclude_sml_ids", set())
            )[self]["forecast_weight"]
            # check if enough space
            if package and package.package_type_id:
                # check weight
                package_smls = self.env["stock.move.line"].search(
                    [
                        ("result_package_id", "=", package.id),
                        ("state", "not in", ["done", "cancel"]),
                    ]
                )
                if self.storage_category_id.max_weight < forecast_weight + sum(
                    package_smls.mapped(
                        lambda sml: sml.quantity_product_uom * sml.product_id.weight
                    )
                ):
                    return "weight"
                # check if enough space
                package_capacity = (
                    self.storage_category_id.package_capacity_ids.filtered(
                        lambda pc: pc.package_type_id == package.package_type_id
                    )
                )
                if package_capacity and location_qty >= package_capacity.quantity:
                    return "capacity"
            else:
                # check weight
                if (
                    self.storage_category_id.max_weight
                    < forecast_weight + product.weight * quantity
                ):
                    return "weight"
                product_capacity = (
                    self.storage_category_id.product_capacity_ids.filtered(
                        lambda pc: pc.product_id == product
                    )
                )
                # To handle new line without quantity in order to avoid suggesting a
                # location already full
                if product_capacity and location_qty >= product_capacity.quantity:
                    return "capacity"
                if (
                    product_capacity
                    and quantity + location_qty > product_capacity.quantity
                ):
                    return "capacity"
            positive_quant = self.quant_ids.filtered(
                lambda q: float_compare(
                    q.quantity, 0, precision_rounding=q.product_id.uom_id.rounding
                )
                > 0
            )
            # check if only allow new product when empty
            if self.storage_category_id.allow_new_product == "empty" and positive_quant:
                return "product"
            # check if only allow same product
            if self.storage_category_id.allow_new_product == "same":
                # In case it's a package, `product` is not defined, so try to get
                # the package products from the context
                product = product or self._context.get("products")
                if (positive_quant and positive_quant.product_id != product) or len(
                    product
                ) > 1:
                    return "product"
                if self.env["stock.move.line"].search(
                    [
                        ("product_id", "!=", product.id),
                        ("state", "not in", ("done", "cancel")),
                        ("location_dest_id", "=", self.id),
                    ],
                    limit=1,
                ):
                    return "product"
        return False

    def _get_volume(self, excluded_sml_ids=False):
        # C&P de Odoo _get_weight modificando peso por volumen
        """Returns a dictionary with the net and forecasted volume of the location.
        param excluded_sml_ids: set of stock.move.line ids to exclude from the
        computation
        """
        result = defaultdict(lambda: defaultdict(float))
        if not excluded_sml_ids:
            excluded_sml_ids = set()
        for location in self:
            for quant in location.quant_ids:
                result[location]["volume"] += quant.product_id.volume * quant.quantity
            result[location]["forecast_volume"] = result[location]["volume"]
            for line in location.incoming_move_line_ids:
                if (
                    line.state in ["draft", "done", "cancel"]
                    or line.id in excluded_sml_ids
                ):
                    continue
                result[location]["forecast_volume"] += (
                    line.product_id.volume * line.quantity_product_uom
                )
            for line in location.outgoing_move_line_ids:
                if (
                    line.state in ["draft", "done", "cancel"]
                    or line.id in excluded_sml_ids
                ):
                    continue
                result[location]["forecast_volume"] -= (
                    line.product_id.volume * line.quantity_product_uom
                )
        return result

    def _check_can_be_used(self, product, quantity=0, package=None, location_qty=0):
        res = super()._check_can_be_used(product, quantity, package, location_qty)
        if not res or float_is_zero(
            self.storage_category_id.max_volume,
            precision_digits=self.env["decimal.precision"].precision_get("Volume"),
        ):
            return res
        forecast_volume = self._get_volume(
            self.env.context.get("exclude_sml_ids", set())
        )[self]["forecast_volume"]
        if package and package.package_type_id:
            package_smls = self.env["stock.move.line"].search(
                [
                    ("result_package_id", "=", package.id),
                    ("state", "not in", ["done", "cancel"]),
                ]
            )
            if self.storage_category_id.max_volume < forecast_volume + sum(
                [
                    sml.quantity_product_uom + sml.product_id.volume
                    for sml in package_smls
                ]
            ):
                return False
        else:
            if (
                self.storage_category_id.max_volume
                < forecast_volume + product.volume * quantity
            ):
                return False
        return res

    def _get_weight(self, excluded_sml_ids=False):
        # Sobreescribimos la función de base porque a nivel de rendimiento apesta
        """Returns a dictionary with the net and forecasted weight of the location.
        param excluded_sml_ids: set of stock.move.line ids to exclude from the
        computation
        """
        result = defaultdict(lambda: defaultdict(float))
        if not excluded_sml_ids:
            excluded_sml_ids = set()
        for location in self:
            result[location] = {"weight": 0.0, "forecast_weight": 0.0}
            if (
                not location.storage_category_id
                or not location.storage_category_id.max_weight
            ):
                continue
            for quant in location.quant_ids:
                result[location]["weight"] += quant.product_id.weight * quant.quantity
            result[location]["forecast_weight"] = result[location]["weight"]
            for line in location.incoming_move_line_ids:
                if (
                    line.state in ["draft", "done", "cancel"]
                    or line.id in excluded_sml_ids
                ):
                    continue
                result[location]["forecast_weight"] += (
                    line.product_id.weight * line.quantity_product_uom
                )
            for line in location.outgoing_move_line_ids:
                if (
                    line.state in ["draft", "done", "cancel"]
                    or line.id in excluded_sml_ids
                ):
                    continue
                result[location]["forecast_weight"] -= (
                    line.product_id.weight * line.quantity_product_uom
                )
        return result
