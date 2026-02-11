/** @odoo-module **/

import BarcodePickingModel from "@stock_barcode/models/barcode_picking_model";

import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

patch(BarcodePickingModel.prototype, {
    get displayAddNewProduct() {
        return this.config.add_new_product;
    },

    allow_scan_extra_qty() {
        return (
            this.config.allow_scan_extra_qty ||
            this.record.immediate_transfer ||
            this.force_create_new_line
        );
    },

    async _createNewLine(params) {
        if (!this.allow_scan_extra_qty()) {
            if (params.fieldsParams.product_id) {
                this.notification(
                    "No puede añadir más unidades más unidades del producto " +
                        params.fieldsParams.product_id.display_name +
                        " de las que hay demandadas",
                    {type: "danger"}
                );
                return false;
            } else if (params.copyOf.product_id) {
                this.notification(
                    "No puede añadir más unidades más unidades del producto " +
                        params.copyOf.product_id.display_name +
                        " de las que hay demandadas",
                    {type: "danger"}
                );
                return false;
            }
        }
        return await super._createNewLine(params);
    },

    async splitLine(line) {
        this.force_create_new_line = true;
        var res = await super.splitLine(line);
        this.force_create_new_line = false;
        return res;
    },

    _updateLineQty(line, args) {
        if (
            !this.allow_scan_extra_qty() &&
            args.qty_done &&
            args.qty_done + line.qty_done > line.reserved_uom_qty
        ) {
            args.qty_done = line.reserved_uom_qty - line.qty_done;
        }
        return super._updateLineQty(line, args);
    },

    async _processPackage(barcodeData) {
        const self = this;
        const stopped = barcodeData.stopped;
        const res = await super._processPackage(barcodeData);
        const recPackage = barcodeData.package;
        if (!stopped && recPackage && barcodeData.stopped) {
            await self._assign_dest_package(barcodeData);
        }
        return res;
    },

    // eslint-disable-next-line complexity
    async _assign_dest_package(packageData) {
        const {packageName} = packageData;
        const recPackage = packageData.package;
        if (
            packageData.error ||
            (packageData.packageType && !recPackage) ||
            (packageName && !recPackage) ||
            !recPackage ||
            (recPackage.location_id &&
                ![this._defaultDestLocation().id, this.location.id].includes(
                    recPackage.location_id
                )) ||
            (this.location && this.location.id !== recPackage.location_id)
        ) {
            return;
        }
        const result = await this.orm.call(
            "stock.quant",
            "get_stock_barcode_data_records",
            [recPackage.quant_ids]
        );
        this.cache.setCache(result.records);
        const quants = result.records["stock.quant"];
        const currentLine = this.selectedLine || this.lastScannedLine;
        if (
            currentLine &&
            (!quants.length ||
                (!currentLine.result_package_id &&
                    recPackage.location_id === currentLine.location_dest_id.id))
        ) {
            return;
        }

        let package_ok = true;
        const quantPackage = packageData.package;
        const package_lines = [];
        if (!quants.length) {
            package_ok = false;
        }
        const fieldsParams = this._convertDataToFieldsParams({
            resultPackage: recPackage,
        });
        for (const quant of quants) {
            const product = this.cache.getRecord("product.product", quant.product_id);
            const lot = quant.lot_id
                ? this.cache.getRecord("stock.lot", quant.lot_id)
                : false;
            const dataLotName = packageData.lotName || (lot && lot.name) || false;

            let remaining_qty = quant.quantity;
            for (const line of this.pageLines) {
                const lineLotName =
                    line.lot_name || (line.lot_id && line.lot_id.name) || false;
                if (
                    line.product_id.id !== product.id ||
                    (quantPackage &&
                        (!line.package_id || line.package_id.id !== quantPackage.id)) ||
                    (dataLotName &&
                        lineLotName &&
                        dataLotName !== lineLotName &&
                        !this._canOverrideTrackingNumber(line)) ||
                    (dataLotName &&
                        line.id &&
                        !line.lot_id &&
                        this.params.model === "stock.quant")
                ) {
                    continue;
                }
                remaining_qty -= line.qty_done;
                package_lines.push(line);
                if (remaining_qty <= 0) {
                    break;
                }
            }
            if (remaining_qty > 0) {
                for (const pack_line of this.packageLines) {
                    if (pack_line.package_id.id !== quantPackage.id) {
                        continue;
                    }
                    for (const line_in_pack of pack_line.lines) {
                        const lineLotName =
                            line_in_pack.lot_name ||
                            (line_in_pack.lot_id && line_in_pack.lot_id.name) ||
                            false;
                        // eslint-disable-next-line max-depth
                        if (
                            line_in_pack.product_id.id !== product.id ||
                            (quantPackage &&
                                (!line_in_pack.package_id ||
                                    line_in_pack.package_id.id !== quantPackage.id)) ||
                            (dataLotName &&
                                lineLotName &&
                                dataLotName !== lineLotName &&
                                !this._canOverrideTrackingNumber(line_in_pack)) ||
                            (dataLotName &&
                                line_in_pack.id &&
                                !line_in_pack.lot_id &&
                                this.params.model === "stock.quant")
                        ) {
                            continue;
                        }
                        remaining_qty -= line_in_pack.qty_done;
                        // eslint-disable-next-line max-depth
                        if (remaining_qty <= 0) {
                            break;
                        }
                    }
                }
                if (remaining_qty > 0) {
                    package_ok = false;
                    break;
                }
            }
        }
        if (package_ok) {
            for (const line of package_lines) {
                await this.updateLine(line, fieldsParams);
            }
            await this.trigger("update");
        }
        return;
    },

    async _parseBarcode(barcode, filters) {
        const barcodeData = await super._parseBarcode(barcode, filters);
        if (!barcodeData.match) {
            return barcodeData;
        }
        const {product, packaging, lot} = barcodeData;
        if (lot && (product || packaging)) {
            const product_id = product ? product.id : packaging.product_id;
            if (lot.product_id !== product_id) {
                const product_lot = await this.cache.getRecordByBarcode(
                    lot.name,
                    "stock.lot",
                    false,
                    {"stock.lot": {product_id: product_id}}
                );
                if (product_lot) {
                    barcodeData.lot = product_lot;
                }
            }
        }
        return barcodeData;
    },

    // eslint-disable-next-line complexity
    async _processLocationDestination(barcodeData) {
        if (
            barcodeData.destLocation &&
            barcodeData.destLocation.id &&
            this.config.restrict_scan_dest_location !== "no"
        ) {
            const lines_to_upd = [];
            const last_scanned_package_id = this.lastScanned.packageId;
            if (this.config.apply_dest_location_all_lines) {
                for (const line of this.pageLines) {
                    if (line.qty_done) {
                        lines_to_upd.push(line);
                    }
                }
            } else if (last_scanned_package_id) {
                const pack_lines = this.pageLines.filter(
                    (l) =>
                        l.result_package_id.id === last_scanned_package_id ||
                        l.package_id.id === last_scanned_package_id
                );
                for (const pack_line of pack_lines) {
                    if (
                        pack_line.qty_done &&
                        pack_line.location_dest_id.id !== barcodeData.destLocation.id
                    ) {
                        lines_to_upd.push(pack_line);
                    }
                }
            }
            if (lines_to_upd.length) {
                if (!this.config.allow_any_dest_location) {
                    if (
                        this._useReservation &&
                        !this._isSublocation(
                            barcodeData.destLocation,
                            this._defaultDestLocation()
                        )
                    ) {
                        barcodeData.stopped = true;
                        const message = _t(
                            "The scanned location doesn't belong to this operation's destination"
                        );
                        return this.notification(message, {type: "danger"});
                    }
                }
                for (const line of lines_to_upd) {
                    await this.changeDestinationLocation(
                        barcodeData.destLocation.id,
                        line
                    );
                }
                barcodeData.stopped = true;
                return;
            }
            if (this.config.allow_any_dest_location) {
                // C&P de enterprise sin restricción por ubi hija
                const lines = this._getLinesToMove();
                for (const line of lines) {
                    await this.changeDestinationLocation(
                        barcodeData.destLocation.id,
                        line
                    );
                }
                barcodeData.stopped = true;
                return;
            }
        }
        return await super._processLocationDestination(barcodeData);
    },

    _checkBarcode(barcodeData) {
        if (
            this.config.restrict_scan_source_location &&
            this.config.stock_barcode_restrict_location
        ) {
            if (barcodeData.location) {
                const isValidLocation = this.pageLines.some(
                    (l) => l.location_id.id === barcodeData.location.id
                );
                if (!isValidLocation) {
                    return {
                        error: true,
                        message: _t(
                            "The scanned location is not available in this operation. Please scan the correct location."
                        ),
                    };
                }
            } else if (barcodeData.product) {
                if (!this.location) {
                    return {
                        error: true,
                        message: _t("Please scan the origin location first."),
                    };
                }
                const productLines = this.pageLines.filter(
                    (l) => l.product_id.id === barcodeData.product.id
                );
                if (
                    productLines.length &&
                    !productLines.some((l) => l.location_id.id === this.location.id)
                ) {
                    return {
                        error: true,
                        message: _t(
                            "The scanned product belongs to another location. Please scan the correct location first."
                        ),
                    };
                }
            }
        }
        let product_updated = false;
        if (
            this.config.restrict_scan_product &&
            barcodeData.packaging &&
            !barcodeData.product
        ) {
            // Con que tenga algo nos vale para que no de error
            barcodeData.product = true;
            product_updated = true;
        }
        const res = super._checkBarcode(barcodeData);
        if (product_updated) {
            delete barcodeData.product;
        }
        return res;
    },

    getDisplayIncrementBtn(line) {
        const superRes = super.getDisplayIncrementBtn(line);
        return this._check_restrict_scan_product_and_location(superRes, line);
    },

    getDisplayIncrementPackagingBtn(line) {
        const superRes = super.getDisplayIncrementPackagingBtn(line);
        return this._check_restrict_scan_product_and_location(superRes, line);
    },

    lineCanBeEdited(line) {
        const superRes = super.lineCanBeEdited(line);
        return this._check_restrict_scan_product_and_location(superRes, line);
    },

    _check_restrict_scan_product_and_location(superRes, line) {
        if (
            !superRes ||
            !this.config.restrict_scan_product ||
            !(
                this.config.restrict_scan_source_location &&
                this.config.stock_barcode_restrict_location
            )
        ) {
            return superRes;
        }
        if (this.location && line.location_id.id !== this.location.id) {
            return false;
        }
        return superRes;
    },
});
