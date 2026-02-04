/** @odoo-module **/

import BarcodeQuantModel from "@stock_barcode/models/barcode_quant_model";
import {patch} from "@web/core/utils/patch";
import {serializeDateTime} from "@web/core/l10n/dates";
/* eslint-disable no-undef */
const {DateTime} = luxon;

function getFormattedDate(value) {
    // Convert to noon to avoid most timezone issues
    const date = DateTime.fromJSDate(value).set({hours: 12, minutes: 0, seconds: 0});
    return serializeDateTime(date);
}

patch(BarcodeQuantModel.prototype, {
    async updateLine(line, args) {
        super.updateLine(...arguments);
        if (args.expiration_date) {
            line.expiration_date = args.expiration_date;
        }
        if (args.use_date) {
            line.use_date = args.use_date;
        }
    },

    async _processGs1Data(data) {
        const result = {};
        const {rule, value} = data;
        if (rule.type === "expiration_date") {
            result.expirationDate = getFormattedDate(value);
            result.match = true;
        } else if (rule.type === "use_date") {
            result.useDate = value;
            result.match = true;
        } else {
            return await super._processGs1Data(...arguments);
        }
        return result;
    },

    /* eslint-disable no-unused-vars */
    async _parseBarcode(barcode, filters) {
        const barcodeData = await super._parseBarcode(...arguments);
        const {product, useDate, expirationDate} = barcodeData;
        if (product && useDate && !expirationDate) {
            const value = new Date(useDate);
            value.setDate(useDate.getDate() + product.use_time);
            barcodeData.expirationDate = getFormattedDate(value);
        }
        if (barcodeData.useDate) {
            barcodeData.useDate = getFormattedDate(useDate);
        }
        return barcodeData;
    },

    _convertDataToFieldsParams(args) {
        const params = super._convertDataToFieldsParams(...arguments);
        if (args.expirationDate) {
            params.expiration_date = args.expirationDate;
        }
        if (args.useDate) {
            params.use_date = args.useDate;
        }
        return params;
    },

    _getFieldToWrite() {
        const fields = super._getFieldToWrite(...arguments);
        fields.push("expiration_date");
        fields.push("use_date");
        return fields;
    },

    _createCommandVals(line) {
        const values = super._createCommandVals(...arguments);
        if (line.expiration_date) {
            values.expiration_date = line.expiration_date;
        }
        if (line.use_date) {
            values.use_date = line.use_date;
        }
        return values;
    },
});
