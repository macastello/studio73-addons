# Copyright 2024 Studio73 - Óscar Seguí <oscar@studio73.es>
# Copyright 2024 Studio73 - Arantxa Gandia <arantxa@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from datetime import timedelta

import requests

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools import html_escape, zeep

from odoo.addons.l10n_es_edi_sii.models.account_edi_format import PatchedHTTPAdapter


class AccountEdiFormat(models.Model):
    _inherit = "account.edi.format"

    def _get_move_applicability(self, move):
        res = super()._get_move_applicability(move)
        if move.l10n_es_edi_is_required:
            errors = self._check_move_configuration(move)
            if errors:
                raise UserError(
                    _(
                        "La configuración de la factura es inválida:\n\n%s",
                        "\n".join(errors),
                    )
                )
            if self.env.context.get("skip_account_edi_cron_trigger", False):
                self._l10n_es_edi_sii_post_invoices_cron(move)
                return False
        return res

    def _l10n_es_edi_sii_post_invoices_cron(self, invoices):
        trigger_obj = self.env["ir.cron.trigger"]
        cron_id = self.env.ref(
            "l10n_es_edi_sii_usability.invoice_process_sii_cron_triggers"
        ).id
        for invoice in invoices:
            if invoice.company_id.sii_send_mode == "auto":
                call_at = fields.Datetime.now()
            elif invoice.company_id.sii_send_mode == "fix_time":
                if invoice.company_id.sii_send_time > fields.Datetime.now().hour:
                    call_at = fields.Datetime.now().replace(
                        hour=int(invoice.company_id.sii_send_time), minute=0, second=0
                    )
                else:
                    call_at = fields.Datetime.now() + timedelta(days=1)
                    call_at = call_at.replace(
                        hour=int(invoice.company_id.sii_send_time), minute=0, second=0
                    )
            elif invoice.company_id.sii_send_mode == "delayed":
                call_at = fields.Datetime.now() + timedelta(
                    hours=invoice.company_id.sii_delay_time
                )
            trigger = trigger_obj.create({"call_at": call_at, "cron_id": cron_id})
            invoice.write(
                {"sii_send_date": call_at, "sii_cron_trigger_ids": [(4, trigger.id)]}
            )

    # flake8: noqa: C901
    def _l10n_es_edi_call_web_service_sign_common(
        self, invoices, info_list, cancel=False
    ):
        company = invoices.company_id

        # All are sharing the same value.
        csv_number = invoices.mapped("l10n_es_edi_csv")[0]

        # Set registration date
        invoices.filtered(lambda inv: not inv.l10n_es_registration_date).write(
            {
                "l10n_es_registration_date": fields.Date.context_today(self),
            }
        )

        # === Call the web service ===

        # Get connection data.
        l10n_es_edi_tax_agency = company.mapped("l10n_es_edi_tax_agency")[0]
        connection_vals = getattr(
            self, f"_l10n_es_edi_web_service_{l10n_es_edi_tax_agency}_vals"
        )(invoices)

        header = {
            "IDVersionSii": "1.1",
            "Titular": {
                "NombreRazon": company.name[:120],
                "NIF": company.vat[2:],
            },
            "TipoComunicacion": "A1" if csv_number else "A0",
        }

        session = requests.Session()
        session.cert = company.l10n_es_edi_certificate_id
        session.mount("https://", PatchedHTTPAdapter())

        client = zeep.Client(
            connection_vals["url"], operation_timeout=60, timeout=60, session=session
        )

        if invoices[0].is_sale_document():
            service_name = "SuministroFactEmitidas"
        else:
            service_name = "SuministroFactRecibidas"
        if company.l10n_es_edi_test_env and not connection_vals.get("test_url"):
            service_name += "Pruebas"

        # Establish the connection.
        serv = client.bind("siiService", service_name)
        if company.l10n_es_edi_test_env and connection_vals.get("test_url"):
            serv._binding_options["address"] = connection_vals["test_url"]

        error_msg = None
        try:
            if cancel:
                if invoices[0].is_sale_document():
                    res = serv.AnulacionLRFacturasEmitidas(header, info_list)
                else:
                    res = serv.AnulacionLRFacturasRecibidas(header, info_list)
            else:
                if invoices[0].is_sale_document():
                    res = serv.SuministroLRFacturasEmitidas(header, info_list)
                else:
                    res = serv.SuministroLRFacturasRecibidas(header, info_list)
        except requests.exceptions.SSLError:
            error_msg = _("The SSL certificate could not be validated.")
        except (zeep.exceptions.Error, requests.exceptions.ConnectionError) as error:
            error_msg = _("Networking error:\n%s", error)
        except Exception as error:
            error_msg = str(error)

        if error_msg:
            return {
                inv: {
                    "error": error_msg,
                    "blocking_level": "warning",
                }
                for inv in invoices
            }

        # Process response.

        if not res or not res.RespuestaLinea:
            return {
                inv: {
                    "error": _("The web service is not responding"),
                    "blocking_level": "warning",
                }
                for inv in invoices
            }

        resp_state = res["EstadoEnvio"]
        l10n_es_edi_csv = res["CSV"]

        if resp_state == "Correcto":
            invoices.write(
                {
                    # Se añade por Studio73 esta funcionalidad para el header que
                    # enviamos  y la respuesta que nos da el SII
                    "l10n_es_edi_csv": l10n_es_edi_csv,
                    "sii_sent_response": res,
                    "sii_sent_header": info_list,
                    # Se terminar nueva funcionalidad
                }
            )
            return {inv: {"success": True} for inv in invoices}

        results = {}
        for respl in res.RespuestaLinea:
            invoice_number = respl.IDFactura.NumSerieFacturaEmisor

            # Retrieve the corresponding invoice.
            # Note: ref can be the same for different partners but there is no enough
            # information on the response
            # to match the partner.

            # Note: Invoices are batched per move_type.
            if invoices[0].is_sale_document():
                inv = invoices.filtered(lambda x: x.name[:60] == invoice_number)  # noqa: B023
            else:
                # 'ref' can be the same for different partners.
                candidates = invoices.filtered(lambda x: x.ref[:60] == invoice_number)  # noqa: B023
                if len(candidates) > 1:
                    respl_partner_info = respl.IDFactura.IDEmisorFactura
                    inv = None
                    for candidate in candidates:
                        partner = candidate.commercial_partner_id
                        if candidate._l10n_es_is_dua():
                            partner = candidate.company_id.partner_id
                        partner_info = self._l10n_es_edi_get_partner_info(partner)
                        if (
                            partner_info.get("NIF")
                            and partner_info["NIF"] == respl_partner_info.NIF
                        ):
                            inv = candidate
                            break
                        if partner_info.get("IDOtro") and all(
                            getattr(respl_partner_info.IDOtro, k) == v
                            for k, v in partner_info["IDOtro"].items()
                        ):
                            inv = candidate
                            break

                    if not inv:
                        # This case shouldn't happen and means there is something
                        #  wrong in this code. However, we can't
                        # raise anything since the document has already been
                        # approved by the government. The result
                        # will only be a badly logged message into the
                        # chatter so, not a big deal.
                        inv = candidates[0]
                else:
                    inv = candidates

            resp_line_state = respl.EstadoRegistro
            respl_dict = dict(respl)
            if resp_line_state in ("Correcto", "AceptadoConErrores"):
                inv.l10n_es_edi_csv = l10n_es_edi_csv
                results[inv] = {"success": True}
                if resp_line_state == "AceptadoConErrores":
                    inv.message_post(
                        body=_("This was accepted with errors: ")
                        + html_escape(respl.DescripcionErrorRegistro)
                    )
            elif (
                respl_dict.get("RegistroDuplicado")
                and respl.RegistroDuplicado.EstadoRegistro == "Correcta"
            ) or (cancel and respl_dict.get("CodigoErrorRegistro") == 3001):
                results[inv] = {"success": True}
                inv.message_post(
                    body=_(
                        "We saw that this invoice was sent correctly before,"
                        " but we did not treat "
                        "the response.  Make sure it is not because of a wrong "
                        "configuration."
                    )
                )

            elif respl.CodigoErrorRegistro == 1117 and not self.env.context.get(
                "error_1117"
            ):
                return self.with_context(
                    error_1117=True
                )._l10n_es_edi_sii_post_invoices(invoices)

            else:
                # Se añade por Studio73 esta funcionalidad para cojer el error que nos
                # da cuando enviamos al SII
                invoices.write({"sii_state": "error"})
                # Se terminar nueva funcionalidad
                results[inv] = {
                    "error": _(
                        "[%s] %s",
                        respl.CodigoErrorRegistro,
                        respl.DescripcionErrorRegistro,
                    ),
                    "blocking_level": "error",
                }

        return results

    def _l10n_es_edi_get_invoices_info(self, invoices):  # noqa: C901
        info_list = []
        for invoice in invoices:
            com_partner = invoice.commercial_partner_id

            if invoice.sii_dua_invoice:
                com_partner = self.env.company.partner_id

            is_simplified = invoice.l10n_es_is_simplified

            info = {
                "PeriodoLiquidacion": {
                    "Ejercicio": str(invoice.date.year),
                    "Periodo": str(invoice.date.month).zfill(2),
                },
                "IDFactura": {
                    "FechaExpedicionFacturaEmisor": invoice.invoice_date.strftime(
                        "%d-%m-%Y"
                    ),
                },
            }

            if invoice.is_sale_document():
                invoice_node = info["FacturaExpedida"] = {}
            else:
                invoice_node = info["FacturaRecibida"] = {}

            # === Partner ===

            partner_info = self._l10n_es_edi_get_partner_info(com_partner)

            # === Invoice ===

            if (
                invoice.delivery_date
                and invoice.delivery_date != invoice.invoice_date
                and not invoice.company_id.l10n_es_edi_force_invoice_date
            ):
                invoice_node["FechaOperacion"] = invoice.delivery_date.strftime(
                    "%d-%m-%Y"
                )
            if invoice.company_id.l10n_es_edi_force_invoice_date:
                invoice_node["FechaOperacion"] = invoice.invoice_date.strftime(
                    "%d-%m-%Y"
                )
            invoice_node["DescripcionOperacion"] = (
                invoice.invoice_origin[:500] if invoice.invoice_origin else "manual"
            )
            reagyp = invoice.invoice_line_ids.tax_ids.filtered(
                lambda t: t.l10n_es_type == "sujeto_agricultura"
            )
            if invoice.is_sale_document():
                nif = (
                    invoice.company_id.vat[2:]
                    if invoice.company_id.vat.startswith("ES")
                    else invoice.company_id.vat
                )
                info["IDFactura"]["IDEmisorFactura"] = {"NIF": nif}
                info["IDFactura"]["NumSerieFacturaEmisor"] = invoice.name[:60]
                if not is_simplified:
                    invoice_node["Contraparte"] = {
                        **partner_info,
                        "NombreRazon": com_partner.name[:120],
                    }
                export_exempts = False
                if (
                    com_partner.country_code == "ES"
                    and com_partner.state_id.code not in ["CE", "ME", "CN", "GC", "TF"]
                ):
                    export_exempts = invoice.invoice_line_ids.tax_ids.filtered(
                        lambda t: t.l10n_es_exempt_reason == "E2"
                    )
                elif com_partner.country_code == "ES" and com_partner.state_id.code in [
                    "CE",
                    "ME",
                    "CN",
                    "GC",
                    "TF",
                ]:
                    export_exempts = True
                elif com_partner.country_code not in [
                    "DE",
                    "BE",
                    "HR",
                    "DK",
                    "ES",
                    "FR",
                    "IE",
                    "LV",
                    "LU",
                    "SE",
                    "BG",
                    "SK",
                    "EE",
                    "GR",
                    "MT",
                    "PL",
                    "CZ",
                    "AT",
                    "CY",
                    "SI",
                    "FI",
                    "HU",
                    "IT",
                    "LT",
                    "PT",
                    "RO",
                ]:
                    export_exempts = invoice.invoice_line_ids.tax_ids.filtered(
                        lambda t: t.l10n_es_exempt_reason == "E2"
                    )
                if (
                    com_partner.country_code == "FR"
                    and com_partner.zip
                    and com_partner.zip[:3]
                    in [
                        "973",
                        "974",
                        "971",
                        "972",
                    ]
                ):
                    export_exempts = invoice.invoice_line_ids.tax_ids.filtered(
                        lambda t: t.l10n_es_exempt_reason == "E2"
                    )
                # If an invoice line contains an OSS tax, the invoice is
                # considered as an OSS operation
                is_oss = self._has_oss_taxes(invoice)
                if is_oss:
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "17"
                elif export_exempts:
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "02"
                else:
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "01"
            else:
                if invoice._l10n_es_is_dua():
                    partner_info = self._l10n_es_edi_get_partner_info(
                        invoice.company_id.partner_id
                    )
                info["IDFactura"]["IDEmisorFactura"] = partner_info
                info["IDFactura"]["IDEmisorFactura"].update(
                    {"NombreRazon": com_partner.name[0:120]}
                )
                info["IDFactura"]["NumSerieFacturaEmisor"] = (invoice.ref or "")[:60]
                if not is_simplified:
                    invoice_node["Contraparte"] = {
                        **partner_info,
                        "NombreRazon": com_partner.name[:120],
                    }

                if invoice.l10n_es_registration_date:
                    invoice_node[
                        "FechaRegContable"
                    ] = invoice.l10n_es_registration_date.strftime("%d-%m-%Y")
                else:
                    invoice_node["FechaRegContable"] = fields.Date.context_today(
                        self
                    ).strftime("%d-%m-%Y")

                mod_303_10 = self.env.ref(
                    "l10n_es.mod_303_casilla_10_balance"
                )._get_matching_tags()
                mod_303_11 = self.env.ref(
                    "l10n_es.mod_303_casilla_11_balance"
                )._get_matching_tags()
                tax_tags = invoice.invoice_line_ids.tax_ids.repartition_line_ids.tag_ids
                intracom = bool(tax_tags & (mod_303_10 + mod_303_11))
                if intracom:
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "09"
                elif reagyp:
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "02"
                else:
                    invoice_node["ClaveRegimenEspecialOTrascendencia"] = "01"

            if invoice.move_type == "out_invoice":
                invoice_node["TipoFactura"] = "F2" if is_simplified else "F1"
            elif invoice.move_type == "out_refund":
                invoice_node["TipoFactura"] = "R5" if is_simplified else "R1"
                invoice_node["TipoRectificativa"] = "I"
            elif invoice.move_type == "in_invoice":
                if reagyp:
                    invoice_node["TipoFactura"] = "F6"
                elif invoice._l10n_es_is_dua():
                    invoice_node["TipoFactura"] = "F5"
                else:
                    invoice_node["TipoFactura"] = "F1"
            elif invoice.move_type == "in_refund":
                invoice_node["TipoFactura"] = "R4"
                invoice_node["TipoRectificativa"] = "I"

            # === Taxes ===

            sign = -1 if invoice.move_type in ("out_refund", "in_refund") else 1

            if invoice.is_sale_document():
                # Customer invoices

                if (
                    com_partner.country_id.code in ("ES", False)
                    and not (com_partner.vat or "").startswith("ESN")
                    or is_simplified
                ):
                    tax_details_info_vals = (
                        self._l10n_es_edi_get_invoices_tax_details_info(invoice)
                    )
                    if (
                        com_partner.country_code == "ES"
                        and com_partner.state_id.code
                        in [
                            "CE",
                            "ME",
                            "CN",
                            "GC",
                            "TF",
                        ]
                    ):
                        # Asegurarse de que existen las claves antes de acceder
                        tax_info = tax_details_info_vals.get("tax_details_info") or {}
                        sujeta = tax_info.get("Sujeta") or {}
                        exenta = sujeta.get("Exenta") or {}
                        detalle_exenta = exenta.get("DetalleExenta") or []
                        for item in detalle_exenta:
                            item.pop("CausaExencion", None)
                    invoice_node["TipoDesglose"] = {
                        "DesgloseFactura": tax_details_info_vals["tax_details_info"]
                    }

                    invoice_node["ImporteTotal"] = round(
                        sign
                        * (
                            tax_details_info_vals["tax_details"]["base_amount"]
                            + tax_details_info_vals["tax_details"]["tax_amount"]
                            - tax_details_info_vals["tax_amount_retention"]
                        ),
                        2,
                    )
                else:
                    tax_details_info_service_vals = (
                        self._l10n_es_edi_get_invoices_tax_details_info(
                            invoice,
                            filter_invl_to_apply=lambda x: any(
                                t.tax_scope == "service" for t in x.tax_ids
                            ),
                        )
                    )
                    tax_details_info_consu_vals = (
                        self._l10n_es_edi_get_invoices_tax_details_info(
                            invoice,
                            filter_invl_to_apply=lambda x: any(
                                t.tax_scope == "consu" for t in x.tax_ids
                            ),
                        )
                    )

                    if tax_details_info_service_vals["tax_details_info"]:
                        invoice_node.setdefault("TipoDesglose", {})
                        invoice_node["TipoDesglose"].setdefault(
                            "DesgloseTipoOperacion", {}
                        )
                        invoice_node["TipoDesglose"]["DesgloseTipoOperacion"][
                            "PrestacionServicios"
                        ] = tax_details_info_service_vals["tax_details_info"]
                    if tax_details_info_consu_vals["tax_details_info"]:
                        invoice_node.setdefault("TipoDesglose", {})
                        invoice_node["TipoDesglose"].setdefault(
                            "DesgloseTipoOperacion", {}
                        )
                        invoice_node["TipoDesglose"]["DesgloseTipoOperacion"][
                            "Entrega"
                        ] = tax_details_info_consu_vals["tax_details_info"]
                    if not invoice_node.get("TipoDesglose"):
                        raise UserError(
                            _(
                                "In case of a foreign customer, you need to configure "
                                "the tax scope on taxes:\n%s",
                                "\n".join(invoice.line_ids.tax_ids.mapped("name")),
                            )
                        )

                    invoice_node["ImporteTotal"] = round(
                        sign
                        * (
                            tax_details_info_service_vals["tax_details"]["base_amount"]
                            + tax_details_info_service_vals["tax_details"]["tax_amount"]
                            - tax_details_info_service_vals["tax_amount_retention"]
                            + tax_details_info_consu_vals["tax_details"]["base_amount"]
                            + tax_details_info_consu_vals["tax_details"]["tax_amount"]
                            - tax_details_info_consu_vals["tax_amount_retention"]
                        ),
                        2,
                    )

            else:
                # Vendor bills

                tax_details_info_isp_vals = (
                    self._l10n_es_edi_get_invoices_tax_details_info(
                        invoice,
                        filter_invl_to_apply=lambda x: any(
                            t for t in x.tax_ids if t.l10n_es_type == "sujeto_isp"
                        ),
                    )
                )
                tax_details_info_other_vals = (
                    self._l10n_es_edi_get_invoices_tax_details_info(
                        invoice,
                        filter_invl_to_apply=lambda x: not any(
                            t for t in x.tax_ids if t.l10n_es_type == "sujeto_isp"
                        ),
                    )
                )

                invoice_node["DesgloseFactura"] = {}
                if tax_details_info_isp_vals["tax_details_info"]:
                    invoice_node["DesgloseFactura"][
                        "InversionSujetoPasivo"
                    ] = tax_details_info_isp_vals["tax_details_info"]
                if tax_details_info_other_vals["tax_details_info"]:
                    invoice_node["DesgloseFactura"][
                        "DesgloseIVA"
                    ] = tax_details_info_other_vals["tax_details_info"]

                if invoice._l10n_es_is_dua() or any(
                    t.l10n_es_type == "ignore" for t in invoice.invoice_line_ids.tax_ids
                ):
                    invoice_node["ImporteTotal"] = round(
                        sign
                        * (
                            tax_details_info_isp_vals["tax_details"]["base_amount"]
                            + tax_details_info_isp_vals["tax_details"]["tax_amount"]
                            + tax_details_info_other_vals["tax_details"]["base_amount"]
                            + tax_details_info_other_vals["tax_details"]["tax_amount"]
                        ),
                        2,
                    )
                else:  # Intra-community -100 repartition line needs
                    # to be taken into account
                    invoice_node["ImporteTotal"] = round(
                        -invoice.amount_total_signed
                        - sign * tax_details_info_isp_vals["tax_amount_retention"]
                        - sign * tax_details_info_other_vals["tax_amount_retention"],
                        2,
                    )

                invoice_node["CuotaDeducible"] = round(
                    sign
                    * (
                        tax_details_info_isp_vals["tax_amount_deductible"]
                        + tax_details_info_other_vals["tax_amount_deductible"]
                    ),
                    2,
                )

            info_list.append(info)
        for info in info_list:
            base_amount_not_subject_loc = (
                info.get("FacturaExpedida", {})
                .get("TipoDesglose", {})
                .get("DesgloseFactura", {})
                .get("NoSujeta", {})
                .get("ImporteTAIReglasLocalizacion", {})
            )
            if base_amount_not_subject_loc:
                info["FacturaExpedida"]["ImporteTotal"] = base_amount_not_subject_loc
        return info_list

    def _l10n_es_edi_sii_send(self, invoices, cancel=False):
        stored_csv = {}
        for inv in invoices:
            if inv.l10n_es_edi_csv:
                stored_csv[inv.id] = inv.l10n_es_edi_csv
        res = super()._l10n_es_edi_sii_send(invoices, cancel=cancel)
        for inv in invoices:
            if inv.id in stored_csv:
                inv.write({"l10n_es_edi_csv": stored_csv[inv.id]})
        return res
