/** @odoo-module **/

import {createWebClient, doAction} from "@web/../tests/webclient/helpers";
import {destroy, getFixture} from "@web/../tests/helpers/utils";

QUnit.module("stock_barcode_usability", {}, function () {
    QUnit.module("Strict Location Scan", {
        beforeEach: function () {
            var self = this;
            this.clientData = {
                action: {
                    tag: "stock_barcode_client_action",
                    type: "ir.actions.client",
                    res_model: "stock.picking",
                    context: {active_id: 1},
                },
                currentState: {
                    actions: {},
                    data: {
                        records: {
                            "barcode.nomenclature": [
                                {
                                    id: 1,
                                    rule_ids: [],
                                },
                            ],
                            "stock.location": [
                                {id: 1, display_name: "Loc 1", barcode: "LOC1"},
                                {id: 2, display_name: "Loc 2", barcode: "LOC2"},
                                {id: 3, display_name: "Loc 3", barcode: "LOC3"},
                            ],
                            "stock.move.line": [
                                {
                                    id: 1,
                                    location_id: 1,
                                    product_id: 1,
                                    qty_done: 0,
                                    reserved_uom_qty: 10,
                                },
                            ],
                            "stock.picking": [
                                {
                                    id: 1,
                                    state: "assigned",
                                    move_line_ids: [1],
                                    location_id: 1,
                                    location_dest_id: 2,
                                    picking_type_id: 1,
                                },
                            ],
                            "product.product": [
                                {id: 1, display_name: "Product A", barcode: "PROD1"},
                            ],
                        },
                        nomenclature_id: 1,
                    },
                    groups: {
                        "stock.group_stock_multi_locations": true,
                    },
                },
            };
            this.mockRPC = function (route) {
                if (route === "/stock_barcode/get_barcode_data") {
                    const result = JSON.parse(
                        JSON.stringify(self.clientData.currentState)
                    );
                    result.config = {
                        restrict_scan_source_location: true,
                        stock_barcode_restrict_location: true,
                        restrict_scan_dest_location: "no",
                        restrict_scan_product: false,
                    };
                    return Promise.resolve(result);
                } else if (route === "/stock_barcode/static/img/barcode.svg") {
                    return Promise.resolve();
                } else if (
                    route === "/web/dataset/call_kw/stock.move/post_barcode_process"
                ) {
                    return Promise.resolve([]);
                }
                return Promise.resolve();
            };
        },
    });

    QUnit.test("strict location scan: block invalid location", async function (assert) {
        assert.expect(1);
        const target = getFixture();
        const webClient = await createWebClient({
            mockRPC: this.mockRPC,
        });
        await doAction(webClient, this.clientData.action);
        webClient.env.services.barcode.bus.trigger("barcode_scanned", {
            barcode: "LOC3",
        });
        await new Promise((resolve) => setTimeout(resolve, 100));
        assert.containsOnce(
            target,
            ".o_notification.border-danger",
            "Should show error notification for invalid location"
        );
        destroy(webClient);
    });

    QUnit.test("strict location scan: allow valid location", async function (assert) {
        assert.expect(1);
        const target = getFixture();
        const webClient = await createWebClient({
            mockRPC: this.mockRPC,
        });
        await doAction(webClient, this.clientData.action);
        webClient.env.services.barcode.bus.trigger("barcode_scanned", {
            barcode: "LOC1",
        });
        await new Promise((resolve) => setTimeout(resolve, 100));
        assert.containsNone(
            target,
            ".o_notification.border-danger",
            "Should NOT show error notification for valid location"
        );
        destroy(webClient);
    });

    QUnit.test(
        "strict location scan: block product scan without location",
        async function (assert) {
            assert.expect(1);
            const target = getFixture();
            const webClient = await createWebClient({
                mockRPC: this.mockRPC,
            });
            await doAction(webClient, this.clientData.action);
            // Escaneamos el producto sin escanear la ubicación primero, debería mostrar un error
            webClient.env.services.barcode.bus.trigger("barcode_scanned", {
                barcode: "PROD1",
            });
            await new Promise((resolve) => setTimeout(resolve, 100));
            assert.containsOnce(
                target,
                ".o_notification.border-danger",
                "Should show error notification when scanning product without location"
            );
            destroy(webClient);
        }
    );

    QUnit.test(
        "strict location scan: block product scan with mismatching location",
        async function (assert) {
            assert.expect(1);
            const target = getFixture();
            const webClient = await createWebClient({
                mockRPC: this.mockRPC,
            });
            await doAction(webClient, this.clientData.action);
            // Escaneamos la ubicación 2 (que no tiene líneas para el producto 1)
            webClient.env.services.barcode.bus.trigger("barcode_scanned", {
                barcode: "LOC2",
            });
            await new Promise((resolve) => setTimeout(resolve, 50));
            // Escaneamos el producto 1, debería mostrar un error
            webClient.env.services.barcode.bus.trigger("barcode_scanned", {
                barcode: "PROD1",
            });
            await new Promise((resolve) => setTimeout(resolve, 100));
            assert.containsOnce(
                target,
                ".o_notification.border-danger",
                "Should show error notification when scanning product in wrong location"
            );
            destroy(webClient);
        }
    );

    QUnit.test(
        "strict location scan: allow product scan with correct location",
        async function (assert) {
            assert.expect(1);
            const target = getFixture();
            const webClient = await createWebClient({
                mockRPC: this.mockRPC,
            });
            await doAction(webClient, this.clientData.action);
            // Escaneamos la ubicación 1 (correct location for Product 1)
            webClient.env.services.barcode.bus.trigger("barcode_scanned", {
                barcode: "LOC1",
            });
            await new Promise((resolve) => setTimeout(resolve, 50));
            // Escaneamos el producto 1, no debería mostrar un error
            webClient.env.services.barcode.bus.trigger("barcode_scanned", {
                barcode: "PROD1",
            });
            await new Promise((resolve) => setTimeout(resolve, 100));
            assert.containsNone(
                target,
                ".o_notification.border-danger",
                "Should NOT show error notification when scanning product in correct location"
            );
            destroy(webClient);
        }
    );
});
