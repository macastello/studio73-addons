/** @odoo-module **/

import {registry} from "@web/core/registry";
import {_t} from "@web/core/l10n/translation";
import {useBus, useService} from "@web/core/utils/hooks";
import * as BarcodeScanner from "@web/webclient/barcode/barcode_scanner";

import {Component} from "@odoo/owl";

export class MainMenuLocationProduct extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.notificationService = useService("notification");
        this.actionService = useService("action");
        this.home = useService("home_menu");
        const barcode = useService("barcode");
        useBus(barcode.bus, "barcode_scanned", this._onBarcodeScanned);
        this.mobileScanner = BarcodeScanner.isBarcodeScannerSupported();
    }

    async _onBarcodeScanned(event) {
        const barcode = event.detail.barcode;
        const res = await this.rpc(
            "/stock_barcode_location_product_info/scan_from_main_menu",
            {barcode}
        );
        if (res.action) {
            return this.actionService.doAction(res.action);
        }
        this.notificationService.add(res.warning, {type: "danger"});
    }

    async openMobileScanner() {
        const barcode = await BarcodeScanner.scanBarcode(this.env);
        if (barcode) {
            this._onBarcodeScanned(barcode);
            if ("vibrate" in window.navigator) {
                window.navigator.vibrate(100);
            }
        } else {
            this.notificationService.add(_t("Please, Scan again!"), {type: "warning"});
        }
    }
}
MainMenuLocationProduct.template = "stock_barcode_location_product_info.MainMenu";

registry
    .category("actions")
    .add("stock_barcode_location_product_main_menu", MainMenuLocationProduct);
