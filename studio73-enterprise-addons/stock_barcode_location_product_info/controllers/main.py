# Copyright 2023 Studio73 - Carlos Reyes <ioan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.http import request

from odoo.addons.stock_barcode.controllers.stock_barcode import StockBarcodeController


class StockBarcodeLocationProduct(StockBarcodeController):
    @http.route(
        "/stock_barcode_location_product_info/scan_from_main_menu",
        type="json",
        auth="user",
    )
    def main_menu_location(self, barcode, **kw):
        barcode_type = None
        nomenclature = request.env.company.nomenclature_id
        if nomenclature.is_gs1_nomenclature:
            parsed_results = nomenclature.parse_barcode(barcode)
            if parsed_results:
                for result in parsed_results[::-1]:
                    if result["rule"].type in [
                        "product",
                        "package",
                        "location",
                        "dest_location",
                    ]:
                        barcode_type = result["rule"].type
                        break
        if not barcode_type or barcode_type == "product":
            ret_open_product_location = self._try_open_product_location(barcode)
            if ret_open_product_location:
                return ret_open_product_location
        ret_open_location = self.try_open_location(barcode)
        if ret_open_location:
            return ret_open_location
        return {
            "warning": "No se ha encontrado ningún producto ni ubicación con el código "
            f"escaneado {barcode}"
        }

    def try_open_location(self, barcode):
        location = request.env["stock.location"].search(
            [("barcode", "=", barcode)], limit=1
        )
        if location:
            return self.get_action(location=location)
        return False

    def get_action(self, location=None):
        action = (
            request.env.ref(
                "stock_barcode_location_product_info.action_stock_quant_minimal_view"
            )
            .sudo()
            .read()[0]
        )
        view_id = (
            request.env.ref(
                "stock_barcode_location_product_info.stock_quant_barcode_kanban_2_inherit"
            )
            .sudo()
            .id
        )
        action.update(
            views=[(view_id, "kanban"), (False, "form")],
        )
        if location:
            action.update(
                domain=[
                    ("location_id", "=", location.id),
                    ("location_id.usage", "=", "internal"),
                ],
                context={"search_default_groupby_product_id": 1, "scan_location": True},
            )
        else:
            return False
        return {"action": action}

    def _try_open_product_location(self, barcode):
        result = super()._try_open_product_location(barcode)
        if result:
            action = result["action"]
            view_id = (
                request.env.ref(
                    "stock_barcode_location_product_info.stock_quant_barcode_kanban_2_inherit"
                )
                .sudo()
                .id
            )
            action["views"] = [(view_id, "kanban"), (action["views"][0][0], "list")]
            action["context"] = {
                "search_default_groupby_location_id": 1,
                "scan_product": True,
            }
            return result
        return False
