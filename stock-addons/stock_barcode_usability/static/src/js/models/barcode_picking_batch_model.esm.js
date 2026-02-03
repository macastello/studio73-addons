/** @odoo-module **/

import BarcodePickingBatchModel from "@stock_barcode_picking_batch/models/barcode_picking_batch_model";

import {patch} from "@web/core/utils/patch";

patch(BarcodePickingBatchModel.prototype, {
    async _closeValidate(ev) {
        if (!this.config.close_partial_batch) {
            return super._closeValidate(ev);
        }
        const record = await this.orm.read(
            "stock.move.line",
            this.record.move_line_ids,
            ["state"]
        );
        let hasDoneLine = false;
        for (const line of record) {
            if (line.state === "done") {
                hasDoneLine = true;
                break;
            }
        }
        if (hasDoneLine) {
            this.notification(this.validateMessage, {type: "success"});
            this.trigger("history-back");
        } else {
            return super._closeValidate(ev);
        }
    },

    groupKey(line) {
        if (this.config && this.config.groupby_loc_and_prod) {
            return `${line.location_id.id}_${line.product_id.id}`;
        }
        return super.groupKey(line);
    },
});
