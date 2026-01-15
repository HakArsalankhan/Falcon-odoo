# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.misc import formatLang


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_report_lines(self):
        """Get journal items excluding sections and notes for report"""
        self.ensure_one()
        return self.line_ids.filtered(lambda l: l.display_type not in ('line_section', 'line_note'))

    def format_amount(self, amount, currency=None):
        """Format amount with currency"""
        if currency is None:
            currency = self.company_currency_id
        return formatLang(self.env, amount, currency_obj=currency, digits=currency.decimal_places)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def get_analytic_distribution_display(self):
        """Format analytic distribution for display"""
        self.ensure_one()
        if not self.analytic_distribution:
            return ''
        # analytic_distribution is a JSON field like {"1": 100} or {"1": 50, "2": 50}
        try:
            if isinstance(self.analytic_distribution, str):
                import json
                dist = json.loads(self.analytic_distribution)
            else:
                dist = self.analytic_distribution
            
            if not dist:
                return ''
            
            parts = []
            for account_id, percentage in dist.items():
                account = self.env['account.analytic.account'].browse(int(account_id))
                if account.exists():
                    parts.append(f"{account.name}: {percentage}%")
            return ', '.join(parts)
        except:
            return ''

    def get_tax_grids_display(self):
        """Format tax grids for display"""
        self.ensure_one()
        if not self.tax_tag_ids:
            return ''
        return ', '.join(self.tax_tag_ids.mapped('name'))

    def get_row_background_color(self, index):
        """Get background color for alternating rows"""
        return '#f8f9fa' if index % 2 == 0 else '#ffffff'

    def get_debit_color(self):
        """Get color for debit amount"""
        return '#28a745' if self.debit > 0 else '#6c757d'

    def get_credit_color(self):
        """Get color for credit amount"""
        return '#dc3545' if self.credit > 0 else '#6c757d'

