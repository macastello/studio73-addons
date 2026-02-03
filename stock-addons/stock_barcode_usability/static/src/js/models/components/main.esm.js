/** @odoo-module **/

import MainComponent from "@stock_barcode/components/main";
import {patch} from "@web/core/utils/patch";

patch(MainComponent.prototype, {
    get displayCounterLines() {
        return (
            this.env.model &&
            this.env.model.lineModel !== "stock.quant" &&
            this.env.model.config &&
            this.env.model.config.show_counter_lines
        );
    },

    get misclines() {
        return this.lines.concat(this.packageLines || []);
    },

    get sublines() {
        return (
            (this.misclines &&
                [].concat(
                    ...this.misclines.map((line) => (line && line.lines) || [])
                )) ||
            []
        );
    },
});
