/** @odoo-module **/

import BarcodeModel from "@stock_barcode/models/barcode_model";

import {patch} from "@web/core/utils/patch";

patch(BarcodeModel.prototype, {
    setData(data) {
        super.setData(...arguments);
        this.force_increment = data.data.force_increment;
    },

    get groupedLines() {
        if (this.config && this.config.avoid_grouped_lines) {
            return this._sortLine(this.pageLines);
        }
        return super.groupedLines;
    },

    _isRestrictedScan(barcodeData) {
        if (!this.config || !this.config.stock_barcode_restrict_products) {
            return false;
        }
        if (barcodeData.product) {
            return !this.currentState.lines.some(
                (line) => line.product_barcode === barcodeData.barcode
            );
        }
        if (barcodeData.package) {
            if (barcodeData.package.package_use === "reusable") {
                return false;
            }
            return !this.currentState.lines.some(
                (line) =>
                    line.result_package_id.name === barcodeData.barcode ||
                    line.package_id.name === barcodeData.barcode
            );
        }
        if (barcodeData.lot) {
            return !this.currentState.lines.some(
                (line) => line.lot_id.name === barcodeData.barcode
            );
        }
        return false;
    },

    async _parseBarcode(barcode, filters) {
        const result = await super._parseBarcode(barcode, filters);
        if (this._isRestrictedScan(result)) {
            return {
                barcode,
                match: false,
            };
        }
        if (
            (["stock.picking", "stock.picking.batch"].includes(this.resModel) &&
                this.lineModel !== "stock.quant" &&
                this.config.force_qty_increment_at_scan &&
                result.product &&
                !result.quantity &&
                !result.destLocation) ||
            (result.quantity === 0 && !result.destLocation)
        ) {
            result.quantity = 1;
        }
        if (this.resModel === "stock.quant" && this.force_increment) {
            result.quantity = 1;
        }
        return result;
    },
});
