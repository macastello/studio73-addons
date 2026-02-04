/** @odoo-module **/

import LineComponent from "@stock_barcode/components/line";
import {patch} from "@web/core/utils/patch";

patch(LineComponent.prototype, {
    get displayPicking() {
        if (this.env.model.config?.groupby_loc_and_prod) {
            return (
                (!this.line.lines || this.props.subline) &&
                this.env.model.resModel === "stock.picking.batch"
            );
        }
        return !this.props.subline && this.env.model.resModel === "stock.picking.batch";
    },
});
