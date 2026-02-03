# Copyright 2018 Studio73 - Abraham Anes <abraham@studio73.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import csv
from contextlib import contextmanager
from io import StringIO

import psycopg2

from odoo import _, exceptions, fields, models

QUERY = """SELECT dense_rank() OVER (
ORDER BY aml.date ASC, aj.code ASC, am.id ASC) as Num_Asiento_Ordenado,
aml.date AS Fecha,
am.id AS Num_Asiento_Odoo,
am.name AS Asiento,
aml.name AS Concepto,
aml.ref AS Referencia,
aa.code AS Cuenta,
aa.name->>'es_ES' AS Nombre_cuenta,
aaa.name AS Cuenta_analitica,
replace(to_char(ROUND(aml.debit, 2), '9999999999D99'), '.', ',') AS Debe,
replace(to_char(ROUND(aml.credit, 2), '9999999999D99'), '.', ',') AS Haber
FROM account_move_line AS aml
  INNER JOIN account_move AS am ON aml.move_id = am.id
  INNER JOIN account_account AS aa ON aml.account_id = aa.id
  INNER JOIN account_journal AS aj ON am.journal_id = aj.id
  LEFT JOIN (
    SELECT rel.account_move_line_id, STRING_AGG(CAST(aaa.name AS text), ', ') AS name
    FROM account_analytic_account as aaa
    INNER JOIN account_analytic_account_account_move_line_rel
    AS rel ON rel.account_analytic_account_id = aaa.id
    GROUP BY rel.account_move_line_id
  ) AS aaa ON aaa.account_move_line_id = aml.id
WHERE am.date>=%s AND
  am.date<=%s AND
  aml.company_id = %s AND
  CASE
    WHEN %s = 'posted' THEN am.state = 'posted'
    ELSE am.id IS NOT NULL
  END"""

QUERY_APERTURA = """SELECT 0 as Num_Asiento_Ordenado,
%s AS Fecha,
0 AS Num_Asiento_Odoo,
'APERTURA' AS Asiento,
'APERTURA' AS Concepto,
'APERTURA' AS Referencia,
aa.code AS Cuenta,
aa.name->>'es_ES' AS Nombre_cuenta,
aaa.name AS Cuenta_analitica,
CASE
    WHEN SUM(aml.debit) > SUM(aml.credit)
        THEN replace(
                to_char(
                    ROUND(SUM(aml.debit) - SUM(aml.credit), 2),
                '9999999999D99'),
            '.', ',')
    WHEN SUM(aml.debit) < SUM(aml.credit)
        THEN '0'
    ELSE
        '0'
END AS Debe,
CASE
    WHEN SUM(aml.debit) > SUM(aml.credit)
        THEN '0'
    WHEN SUM(aml.debit) < SUM(aml.credit)
        THEN replace(
                to_char(
                    ROUND(SUM(aml.credit) - SUM(aml.debit), 2),
                '9999999999D99'),
            '.', ',')
    ELSE
        '0'
END AS Haber
FROM account_move_line AS aml
  INNER JOIN account_move AS am ON aml.move_id = am.id
  INNER JOIN account_account AS aa ON aml.account_id = aa.id
  LEFT JOIN (
    SELECT rel.account_move_line_id, STRING_AGG(CAST(aaa.name AS text), ', ') AS name
    FROM account_analytic_account as aaa
    INNER JOIN account_analytic_account_account_move_line_rel
    AS rel ON rel.account_analytic_account_id = aaa.id
    GROUP BY rel.account_move_line_id
  ) AS aaa ON aaa.account_move_line_id = aml.id
WHERE am.date<%s AND
  aml.company_id = %s AND
  aa.code NOT LIKE '6%%' AND
  aa.code NOT LIKE '7%%' AND
  CASE
    WHEN %s = 'posted' THEN am.state = 'posted'
    ELSE am.id IS NOT NULL
  END
GROUP BY aa.code, aa.name, aaa.name"""

QUERY_APERTURA_REG = """SELECT %s as Num_Asiento_Ordenado,
%s AS Fecha,
%s AS Num_Asiento_Odoo,
'APERTURA' AS Asiento,
'APERTURA' AS Concepto,
'APERTURA' AS Referencia,
RPAD('129', %s, '0') AS Cuenta,
'RESULTADO DEL EJERCICIO' AS Nombre_cuenta,
apertura_reg.cuenta_analitica AS Cuenta_analitica,
CASE
    WHEN debit > credit
        THEN '0'
    WHEN debit < credit
        THEN replace(to_char(ROUND(credit - debit, 2), '9999999999D99'), '.', ',')
    ELSE
        '0'
END AS Debe,
CASE
    WHEN debit > credit
        THEN replace(to_char(ROUND(debit - credit, 2), '9999999999D99'), '.', ',')
    WHEN debit < credit
        THEN '0'
    ELSE
        '0'
END AS Haber
FROM (
  SELECT
    aaa.name as cuenta_analitica,
    SUM(aml.debit) AS debit,
    SUM(aml.credit) AS credit
  FROM account_move_line AS aml
    INNER JOIN account_move AS am ON aml.move_id = am.id
    INNER JOIN account_account AS aa ON aml.account_id = aa.id

  LEFT JOIN (
    SELECT rel.account_move_line_id, STRING_AGG(CAST(aaa.name AS text), ', ') AS name
    FROM account_analytic_account as aaa
    INNER JOIN account_analytic_account_account_move_line_rel
    AS rel ON rel.account_analytic_account_id = aaa.id
    GROUP BY rel.account_move_line_id
  ) AS aaa ON aaa.account_move_line_id = aml.id
  WHERE am.date<%s AND
    aml.company_id = %s AND
    aa.code NOT LIKE '6%%' AND
    aa.code NOT LIKE '7%%' AND
    CASE
      WHEN %s = 'posted' THEN am.state = 'posted'
      ELSE am.id IS NOT NULL
    END
  GROUP BY aaa.name
) AS apertura_reg"""

QUERY_CIERRE = """SELECT 9999999 as Num_Asiento_Ordenado,
%s AS Fecha,
9999999 AS Num_Asiento_Odoo,
'CIERRE' AS Asiento,
'CIERRE' AS Concepto,
'CIERRE' AS Referencia,
aa.code AS Cuenta,
aa.name->>'es_ES' AS Nombre_cuenta,
aaa.name AS Cuenta_analitica,
CASE
    WHEN SUM(aml.debit) > SUM(aml.credit)
        THEN '0'
    WHEN SUM(aml.debit) < SUM(aml.credit)
        THEN replace(
            to_char(
                ROUND(SUM(aml.credit) - SUM(aml.debit), 2),
            '9999999999D99'), '.', ',')
    ELSE
        '0'
END AS Debe,
CASE
    WHEN SUM(aml.debit) > SUM(aml.credit)
        THEN replace(
                to_char(
                    ROUND(SUM(aml.debit) - SUM(aml.credit), 2),
                '9999999999D99'),
            '.', ',')
    WHEN SUM(aml.debit) < SUM(aml.credit)
        THEN '0'
    ELSE
        '0'
END AS Haber
FROM account_move_line AS aml
  INNER JOIN account_move AS am ON aml.move_id = am.id
  INNER JOIN account_account AS aa ON aml.account_id = aa.id

  LEFT JOIN (
    SELECT rel.account_move_line_id, STRING_AGG(CAST(aaa.name AS text), ', ') AS name
    FROM account_analytic_account as aaa
    INNER JOIN account_analytic_account_account_move_line_rel
    AS rel ON rel.account_analytic_account_id = aaa.id
    GROUP BY rel.account_move_line_id
  ) AS aaa ON aaa.account_move_line_id = aml.id
WHERE am.date<=%s AND
  aml.company_id = %s AND
  aa.code NOT LIKE '6%%' AND
  aa.code NOT LIKE '7%%' AND
  CASE
    WHEN %s = 'posted' THEN am.state = 'posted'
    ELSE am.id IS NOT NULL
  END
GROUP BY aa.code, aa.name, aaa.name"""

QUERY_CIERRE_REG = """SELECT %s as Num_Asiento_Ordenado,
%s AS Fecha,
%s AS Num_Asiento_Odoo,
'CIERRE' AS Asiento,
'CIERRE' AS Concepto,
'CIERRE' AS Referencia,
RPAD('129', %s, '0') AS Cuenta,
'RESULTADO DEL EJERCICIO' AS Nombre_cuenta,
cierre_reg.cuenta_analitica AS Cuenta_analitica,
CASE
    WHEN debit > credit
        THEN replace(to_char(ROUND(debit - credit, 2), '9999999999D99'), '.', ',')
    WHEN debit < credit
        THEN '0'
    ELSE
        '0'
END AS Debe,
CASE
    WHEN debit > credit
        THEN '0'
    WHEN debit < credit
        THEN replace(to_char(ROUND(credit - debit, 2), '9999999999D99'), '.', ',')
    ELSE
        '0'
END AS Haber
FROM (
  SELECT
    aaa.name as cuenta_analitica,
    SUM(aml.debit) AS debit,
    SUM(aml.credit) AS credit
  FROM account_move_line AS aml
    INNER JOIN account_move AS am ON aml.move_id = am.id
    INNER JOIN account_account AS aa ON aml.account_id = aa.id

  LEFT JOIN (
    SELECT rel.account_move_line_id, STRING_AGG(CAST(aaa.name AS text), ', ') AS name
    FROM account_analytic_account as aaa
    INNER JOIN account_analytic_account_account_move_line_rel
    AS rel ON rel.account_analytic_account_id = aaa.id
    GROUP BY rel.account_move_line_id
  ) AS aaa ON aaa.account_move_line_id = aml.id
  WHERE am.date<=%s AND
    aml.company_id = %s AND
    aa.code NOT LIKE '6%%' AND
    aa.code NOT LIKE '7%%' AND
    CASE
      WHEN %s = 'posted' THEN am.state = 'posted'
      ELSE am.id IS NOT NULL
    END
  GROUP BY aaa.name
) AS cierre_reg"""

QUERY_PYG = """SELECT 9999998 as Num_Asiento_Ordenado,
%s AS Fecha,
9999998 AS Num_Asiento_Odoo,
'PERDIDAS Y GANANCIAS' AS Asiento,
'PERDIDAS Y GANANCIAS' AS Concepto,
'PERDIDAS Y GANANCIAS' AS Referencia,
aa.code AS Cuenta,
aa.name->>'es_ES' AS Nombre_cuenta,
aaa.name AS Cuenta_analitica,
CASE
    WHEN SUM(aml.debit) > SUM(aml.credit)
        THEN '0'
    WHEN SUM(aml.debit) < SUM(aml.credit)
        THEN replace(
                to_char(
                    ROUND(SUM(aml.credit) - SUM(aml.debit), 2),
                '9999999999D99'),
            '.', ',')
    ELSE
        '0'
END AS Debe,
CASE
    WHEN SUM(aml.debit) > SUM(aml.credit)
        THEN replace(
                to_char(
                    ROUND(SUM(aml.debit) - SUM(aml.credit), 2),
                '9999999999D99'),
            '.', ',')
    WHEN SUM(aml.debit) < SUM(aml.credit)
        THEN '0'
    ELSE
        '0'
END AS Haber
FROM account_move_line AS aml
  INNER JOIN account_move AS am ON aml.move_id = am.id
  INNER JOIN account_account AS aa ON aml.account_id = aa.id

  LEFT JOIN (
    SELECT rel.account_move_line_id, STRING_AGG(CAST(aaa.name AS text), ', ') AS name
    FROM account_analytic_account as aaa
    INNER JOIN account_analytic_account_account_move_line_rel
    AS rel ON rel.account_analytic_account_id = aaa.id
    GROUP BY rel.account_move_line_id
  ) AS aaa ON aaa.account_move_line_id = aml.id
WHERE am.date<=%s AND
  am.date>=%s AND
  aml.company_id = %s AND
  (aa.code LIKE '6%%' OR
   aa.code LIKE '7%%') AND
  CASE
    WHEN %s = 'posted' THEN am.state = 'posted'
    ELSE am.id IS NOT NULL
  END
GROUP BY aa.code, aa.name, aaa.name"""

QUERY_PYG_REG = """SELECT %s as Num_Asiento_Ordenado,
%s AS Fecha,
%s AS Num_Asiento_Odoo,
'PERDIDAS Y GANANCIAS' AS Asiento,
'PERDIDAS Y GANANCIAS' AS Concepto,
'PERDIDAS Y GANANCIAS' AS Referencia,
RPAD('129', %s, '0') AS Cuenta,
'RESULTADO DEL EJERCICIO' AS Nombre_cuenta,
pyg_reg.cuenta_analitica AS Cuenta_analitica,
CASE
    WHEN debit > credit
        THEN replace(to_char(ROUND(debit - credit, 2), '9999999999D99'), '.', ',')
    WHEN debit < credit
        THEN '0'
    ELSE
        '0'
END AS Debe,
CASE
    WHEN debit > credit
        THEN '0'
    WHEN debit < credit
        THEN replace(to_char(ROUND(credit - debit, 2), '9999999999D99'), '.', ',')
    ELSE
        '0'
END AS Haber
FROM (
  SELECT
    aaa.name as cuenta_analitica,
    SUM(aml.debit) AS debit,
    SUM(aml.credit) AS credit
  FROM account_move_line AS aml
    INNER JOIN account_move AS am ON aml.move_id = am.id
    INNER JOIN account_account AS aa ON aml.account_id = aa.id

  LEFT JOIN (
    SELECT rel.account_move_line_id, STRING_AGG(CAST(aaa.name AS text), ', ') AS name
    FROM account_analytic_account as aaa
    INNER JOIN account_analytic_account_account_move_line_rel
    AS rel ON rel.account_analytic_account_id = aaa.id
    GROUP BY rel.account_move_line_id
  ) AS aaa ON aaa.account_move_line_id = aml.id
  WHERE am.date<=%s AND
    am.date>=%s AND
    aml.company_id = %s AND
    (aa.code LIKE '6%%' OR
     aa.code LIKE '7%%') AND
    CASE
      WHEN %s = 'posted' THEN am.state = 'posted'
      ELSE am.id IS NOT NULL
    END
  GROUP BY aaa.name
) AS pyg_reg"""


class AccountAccountingJournal(models.TransientModel):
    _name = "account.accounting_journal"
    _description = "Wizard para el informe de diario de contabilidad"

    date_from = fields.Date(string="Fecha desde", required=True)
    date_to = fields.Date(string="Fecha hasta", required=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Compañia",
        required=True,
        default=lambda self: self.env.company,
    )
    binary_file = fields.Binary("Fichero")
    file_name = fields.Char("Nombre fichero")
    include_opening = fields.Boolean("Incluir apertura")
    include_closing = fields.Boolean("Incluir cierre")
    include_pyg = fields.Boolean("Incluir regularización PyG")
    include_analytic_account = fields.Boolean("Mostrar contabilidad analítica")
    target_move = fields.Selection(
        [("posted", "All Posted Entries"), ("all", "All Entries")],
        string="Target Moves",
        required=True,
        default="posted",
    )
    level = fields.Selection(
        string="Nivel",
        selection=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("99", "Máximo")],
    )

    def _get_account_groups_dict(self):
        return {
            group["code_prefix_start"]: group["name"]
            for group in self.env["account.group"].search_read(
                [("level", "=", int(self.level) - 1)], ("code_prefix_start", "name")
            )
        }

    def _get_account_analytic_dict(self):
        return {
            group["code_prefix_start"]: group["name"]
            for group in self.env["account.move"].search_read(
                [("level", "=", int(self.level) - 1)], ("code_prefix_start", "name")
            )
        }

    def adjust_to_level_csv(self, csv_file):
        if int(self.level) and int(self.level) != 99:
            groups = self._get_account_groups_dict()
            for row in csv_file:
                # row[6] = cuenta, row[7] = nombre de cuenta
                if len(row) >= 6 and row[6].isdigit():
                    row[6] = row[6][: int(self.level)]
                    row[7] = groups.get(row[6], "")
        return csv_file

    def add_company_header(self, csv_file):
        csv_file.insert(0, [f"Libro diario - {self.env.user.company_id.name}"])
        csv_file.insert(1, [])
        return csv_file

    def _csv_to_b64(self, output):
        output.seek(0)
        data = csv.reader(output, delimiter=";")
        csv_file = []
        csv_file.extend(data)
        if not self.include_analytic_account:
            for row in csv_file:
                row.pop(8)
        output.close()
        csv_file = self._rewrite_csv(csv_file)
        new_output = StringIO()
        output_writer = csv.writer(new_output, delimiter=";")
        for row in csv_file:
            output_writer.writerow(row)
        res = base64.b64encode(bytes(new_output.getvalue(), "utf-8"))
        new_output.close()
        return res

    def _rewrite_csv(self, csv_file):
        csv_file = self.adjust_to_level_csv(csv_file)
        csv_file = self.add_company_header(csv_file)
        return csv_file

    def _build_query(self):
        date_to = self.date_to
        date_from = self.date_from
        if date_from > date_to:
            raise exceptions.Warning(
                _('La "Fecha des de" no puede ser mayor que la "Fecha hasta".')
            )
        final_query = ""
        query_params = []
        code_digits = self._get_code_digits_with_chart_template()
        if self.include_opening:
            final_query += (
                QUERY_APERTURA + " UNION ALL " + QUERY_APERTURA_REG + " UNION ALL "
            )
            query_params.extend(
                [
                    date_from,
                    date_from,
                    self.company_id.id,
                    self.target_move,
                    0,
                    date_from,
                    0,
                    code_digits,
                    date_from,
                    self.company_id.id,
                    self.target_move,
                ]
            )

        final_query += QUERY
        query_params.extend([date_from, date_to, self.company_id.id, self.target_move])

        if self.include_pyg:
            final_query += " UNION ALL " + QUERY_PYG + " UNION ALL " + QUERY_PYG_REG
            query_params.extend(
                [
                    date_to,
                    date_to,
                    date_from,
                    self.company_id.id,
                    self.target_move,
                    9999998,
                    date_to,
                    9999998,
                    code_digits,
                    date_to,
                    date_from,
                    self.company_id.id,
                    self.target_move,
                ]
            )

        if self.include_closing:
            final_query += (
                " UNION ALL " + QUERY_CIERRE + " UNION ALL " + QUERY_CIERRE_REG
            )
            query_params.extend(
                [
                    date_to,
                    date_to,
                    self.company_id.id,
                    self.target_move,
                    9999999,
                    date_to,
                    9999999,
                    code_digits,
                    date_to,
                    self.company_id.id,
                    self.target_move,
                ]
            )
        final_query += " ORDER BY Num_Asiento_Ordenado ASC"
        return self.env.cr.mogrify(final_query, query_params).decode("utf-8")

    def _get_code_digits_with_chart_template(self):
        template_code = self.env["account.chart.template"]._guess_chart_template(
            self.company_id.country_id
        )
        data = self.env["account.chart.template"]._get_chart_template_data(
            template_code
        )
        return int(data.pop("template_data").get("code_digits", "0"))

    def export(self):
        self.ensure_one()
        self._build_query()
        query = "COPY ({}) TO STDOUT WITH {}".format(
            self._build_query(), "CSV HEADER DELIMITER ';'"
        )
        output = StringIO()

        @contextmanager
        def _paused_thread():
            try:
                thread = psycopg2.extensions.get_wait_callback()
                psycopg2.extensions.set_wait_callback(None)
                yield
            finally:
                psycopg2.extensions.set_wait_callback(thread)

        with _paused_thread():
            self.env.cr.copy_expert(query, output)
        res = self._csv_to_b64(output)
        self.write({"binary_file": res, "file_name": "DiarioContabilidad.csv"})

        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": "account.accounting_journal",
            "res_id": self.id,
            "type": "ir.actions.act_window",
            "target": "new",
            "context": self._context,
            "nodestroy": True,
        }

    def _adjust_to_level_pdf(self, data):
        if int(self.level) and int(self.level) != 99:
            groups = self._get_account_groups_dict()
            for line in data:
                line["cuenta"] = line["cuenta"][: int(self.level)]
                line["nombre_cuenta"] = groups.get(
                    line["cuenta"], line["nombre_cuenta"]
                )
        return data

    def _adjust_currency(self, data):
        for line in data:
            line.update(
                {
                    "debe": float(line["debe"].replace(",", ".")),
                    "haber": float(line["haber"].replace(",", ".")),
                }
            )
        return data

    def _rewrite_pdf(self, data):
        data = self._adjust_to_level_pdf(data)
        data = self._adjust_currency(data)
        return data

    def export_pdf(self):
        self.ensure_one()
        query = self._build_query()
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchall()
        data = self._rewrite_pdf(data)
        return self.env.ref(
            "account_accounting_journal_report.report_acc_accounting_journal"
        ).report_action(
            self,
            data={
                "data": data,
                "date_from": self.date_from,
                "date_to": self.date_to,
                "level": self.level,
                "include_analytic_account": self.include_analytic_account,
            },
            config=False,
        )
