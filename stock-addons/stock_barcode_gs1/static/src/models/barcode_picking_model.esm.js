/** @odoo-module **/

import BarcodePickingModel from "@stock_barcode/models/barcode_picking_model";
import {patch} from "@web/core/utils/patch";
import {serializeDateTime} from "@web/core/l10n/dates";
/* eslint-disable no-undef */
const {DateTime} = luxon;

function getFormattedDate(value) {
    // Convert to noon to avoid most timezone issues
    const date = DateTime.fromJSDate(value).set({hours: 12, minutes: 0, seconds: 0});
    return serializeDateTime(date);
}

patch(BarcodePickingModel.prototype, {
    async updateLine(line, args) {
        super.updateLine(...arguments);
        if (args.use_date) {
            line.use_date = args.use_date;
        }
    },

    /* eslint-disable no-unused-vars */
    async _parseBarcode(barcode, filters) {
        const barcodeData = await super._parseBarcode(...arguments);
        if (barcodeData.useDate) {
            barcodeData.useDate = getFormattedDate(barcodeData.useDate);
        }
        return barcodeData;
    },

    _convertDataToFieldsParams(args) {
        const params = super._convertDataToFieldsParams(...arguments);
        if (args.useDate) {
            params.use_date = args.useDate;
        }
        return params;
    },

    _getFieldToWrite() {
        const fields = super._getFieldToWrite(...arguments);
        fields.push("use_date");
        return fields;
    },

    _createCommandVals(line) {
        const values = super._createCommandVals(...arguments);
        if (line.use_date) {
            values.use_date = line.use_date;
        }
        return values;
    },
});
