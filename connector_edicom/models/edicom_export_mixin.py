# Copyright 2024 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
import io
import logging
import re
from ftplib import FTP
from tempfile import NamedTemporaryFile

import unidecode

from odoo import _, exceptions, fields, models, tools
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

EXPRESSION_PATTERN = re.compile(r"\$\{([^}]+)\}")


class EdicomExportMixin(models.AbstractModel):
    _name = "edicom.export.mixin"
    _description = "EDICOM export mixin"

    def _format_string(self, text, length, fill=" ", align="<"):
        if not text:
            return fill * length
        text = text.upper()
        ascii_string = unidecode.unidecode(text)
        if len(ascii_string) > length:
            ascii_string = ascii_string[:length]
        if align == "<":
            ascii_string = ascii_string.ljust(length, fill)
        elif align == ">":
            ascii_string = ascii_string.rjust(length, fill)
        else:
            raise exceptions.UserError(_("Invalid alignment option. Use '<' or '>'"))
        if len(ascii_string) != length:
            raise exceptions.UserError(_("Formatted string length mismatch."))
        return ascii_string

    def _format_fiscal_name(self, text, length, fill=" ", align="<"):
        name = re.sub(
            r"[^a-zA-Z0-9\sáÁéÉíÍóÓúÚñÑçÇäÄëËïÏüÜöÖ"
            r"àÀèÈìÌòÒùÙâÂêÊîÎôÔûÛ\.,-_&'´\\:;:/]",
            "",
            text,
            flags=re.UNICODE | re.X,
        )
        name = re.sub(r"\s{2,}", " ", name, flags=re.UNICODE | re.X)
        return self._format_string(name, length, fill=fill, align=align)

    def _format_number(
        self,
        number,
        int_length,
        dec_length=0,
        include_sign=True,
        positive_sign="+",
        negative_sign="-",
    ):
        if number == "":
            number = 0.0
        number = float(number)
        sign = positive_sign if number >= 0 else negative_sign
        number = abs(number)
        int_part = int(number)
        ascii_string = ""
        if include_sign:
            ascii_string += sign
        if dec_length > 0:
            formatted_number = f"{number:0{int_length + dec_length}.{dec_length}f}"
            ascii_string += formatted_number.replace(".", ",")
        elif int_length > 0:
            ascii_string += f"{int_part:0{int_length}d}"
        reserved_size = 1 if include_sign else 0
        expected_length = reserved_size + int_length + dec_length
        if len(ascii_string) != expected_length:
            raise exceptions.UserError(
                _("Formatted string length mismatch. Expected: {}, Got: {}").format(
                    expected_length, len(ascii_string)
                )
            )
        return ascii_string

    def _format_boolean(self, value, yes="X", no=" "):
        return yes if value else no

    def _format_date(self, value, time=False):
        if not value:
            return ""
        if isinstance(value, str) and "." in value:
            value = value.split(".")[0]
        formatd = "%Y%m%d%H%M" if time else "%Y%m%d"
        date = fields.Datetime.from_string(value)
        return date.strftime(formatd)

    def _export_line_process(self, obj, line):
        def _raise_error(msg):
            msg = _(
                "Error while evaluating expression: (%(expression)s) "
                "in line sequence %(sequence)s "
                "of Export Configuration %(export_config_id)s"
            ) % {
                "expression": line.expression,
                "sequence": line.sequence,
                "export_config_id": line.export_config_id.name,
            }
            raise exceptions.UserError(msg)

        obj_merge = obj

        def merge(match):
            exp = match.group(1).strip().replace("\n", "")
            try:
                result = safe_eval(
                    exp,
                    {
                        "user": self.env.user,
                        "object": obj_merge,
                        "context": self.env.context.copy(),
                    },
                )
                return tools.ustr(result) if result or isinstance(result, float) else ""
            except Exception as e:
                _raise_error(e)

        def merge2(expression):
            try:
                result = safe_eval(
                    expression,
                    {
                        "user": self.env.user,
                        "object": obj_merge,
                        "context": self.env.context.copy(),
                    },
                )
                return result or []
            except Exception as e:
                _raise_error(e)

        res = []
        if line.conditional_expression:
            if not EXPRESSION_PATTERN.sub(merge, line.conditional_expression):
                return []
            res.append(self._export_simple_record(line, ""))
            return res

        if line.repeat_expression:
            obj_list = merge2(line.repeat_expression)
        else:
            obj_list = [obj]

        for _obj_merge in obj_list:
            if line.export_type == "subconfig":
                for sub_line in line.sub_config.config_lines:
                    res += self._export_line_process(_obj_merge, sub_line)
                if line.repeat_expression:
                    res.append("\n")
            else:
                if line.expression:
                    field_val = EXPRESSION_PATTERN.sub(merge, line.expression)
                else:
                    if line.sequence == 0:
                        continue
                    field_val = line.fixed_value
                res.append(
                    self._export_simple_record(line, field_val).replace("\n", "")
                )
        return res

    def _export_simple_record(self, line, val):
        if line.export_type == "string":
            return self._format_string(
                val or "", line.size, align=">" if line.alignment == "right" else "<"
            )
        if line.export_type == "boolean":
            return self._format_boolean(val, line.bool_yes, line.bool_no)
        if line.export_type == "datetime":
            return self._format_date(val, time=True)
        if line.export_type == "date":
            return self._format_date(val)
        if not line.required and float(val or 0) == 0.0:
            return ""
        decimal_size = 0 if line.export_type == "integer" else line.decimal_size
        reserved_size = 1 if line.apply_sign else 0
        return self._format_number(
            float(val or 0),
            line.size - decimal_size - reserved_size,
            decimal_size,
            line.apply_sign,
            positive_sign=line.positive_sign,
            negative_sign=line.negative_sign,
        )

    def export_to_edicom(self, records, export_config, export_path=None):
        if not records:
            raise exceptions.UserError(
                _("No se han seleccionado registros para exportar")
            )
        for record in records:
            attachments = self.env["ir.attachment"]
            for export_config_line in export_config.config_lines:
                file_content = io.StringIO()
                contents = self._export_line_process(record, export_config_line)
                file_content.write("".join(contents))
                file_data = base64.b64encode(file_content.getvalue().encode("utf-8"))
                file_content.close()
                file_name = f"{export_config_line.name}.txt"
                attachments += self.env["ir.attachment"].create(
                    {
                        "name": file_name,
                        "type": "binary",
                        "datas": file_data,
                        "res_model": record._name,
                        "res_id": record.id,
                        "mimetype": "text/plain",
                    }
                )
            record.message_post(
                body=_("Exportación EDI completada"),
                message_type="comment",
                subtype_xmlid="mail.mt_note",
                attachment_ids=attachments.ids,
            )
            self.env.cr.commit()
            res = self._export_to_edicom_ftp(
                attachments=attachments, export_path=export_path
            )
            if res:
                record.message_post(
                    body=_("Exportación al servidor Edicom completada"),
                    message_type="comment",
                    subtype_xmlid="mail.mt_note",
                )
        return True

    def _export_to_edicom_ftp(self, attachments=None, export_path=None):
        if attachments is None:
            attachments = self.env["ir.attachment"]
        ftp_connection = self._get_ftp_connection()
        # ftp.storbinary hace el b64encode internamente
        if not export_path:
            export_path = "./PRODUCCION/SALIDA/"
        for attachment in attachments:
            report = base64.b64decode(attachment.datas)
            full_filename = attachment.name
            tmp_file = NamedTemporaryFile()
            tmp_file.write(report)
            tmp_file.seek(0)
            try:
                ftp_connection.storbinary(
                    f"STOR {export_path}{full_filename}", tmp_file
                )
            except Exception as e:
                raise exceptions.UserError(
                    _("Error mientras se intentaba enviar el fichero.\n{}").format(e)
                ) from e
        ftp_connection.quit()
        return True

    def _get_ftp_connection(self):
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("edicom.ftp.connection", "")
        )
        (
            host,
            user,
            passwd,
        ) = param.split(";")
        try:
            ftp = FTP(host)
            ftp.login(user=user, passwd=passwd)
            return ftp
        except Exception as e:
            raise exceptions.UserError(
                _("No se puede realizar la conexión con el servidor FTP\n{}").format(e)
            ) from e
