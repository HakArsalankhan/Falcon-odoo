# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date


class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _description = 'Purchase Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'pr_ref'

    pr_ref = fields.Char(string="PR Ref", readonly=True, copy=False)
    date = fields.Date(string="Date", default=fields.Date.today)
    requested_by_id = fields.Many2one('hr.employee', string="Requested By")
    title_id = fields.Many2one('hr.job', string="Title", related='requested_by_id.job_id', store=True)
    email = fields.Char(string="Email", related='requested_by_id.work_email', store=True)
    to_department_id = fields.Many2one('hr.department', string="To Department")

    serving_client = fields.Char(string="Serving Client")
    po_project = fields.Char(string="PO/Project")

    to_be_purchased_by_id = fields.Many2one('hr.employee', string="To Be Purchased By")
    to_title_id = fields.Many2one('hr.job', string="Title", related='to_be_purchased_by_id.job_id', store=True)
    to_email = fields.Char(string="Email", related='to_be_purchased_by_id.work_email', store=True)
    to_mobile = fields.Char(string="Mobile", related='to_be_purchased_by_id.work_phone', store=True)

    vendor_id = fields.Many2one('res.partner', string="Vendor", domain="[('supplier_rank', '>', 0)]")
    vendor_ref = fields.Char(string="Vendor ID")

    order_line_ids = fields.One2many('purchase.request.line', 'request_id', string="Product Lines")

    amount_untaxed = fields.Monetary(string="Untaxed Amount", compute='_compute_amounts', store=True)
    amount_tax = fields.Monetary(string="Taxes", compute='_compute_amounts', store=True)
    amount_total = fields.Monetary(string="Total", compute='_compute_amounts', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id.id)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company.id
    )
    notes = fields.Char(string="Notes")

    @api.depends('order_line_ids.price_subtotal', 'order_line_ids.taxes_id', 'order_line_ids.product_qty',
                 'order_line_ids.price_unit')
    def _compute_amounts(self):
        for rec in self:
            untaxed = 0.0
            taxes = 0.0
            for line in rec.order_line_ids:
                # Compute taxes using Odoo's built-in function
                tax_data = line.taxes_id.compute_all(
                    line.price_unit,
                    rec.currency_id,
                    line.product_qty,
                    product=line.product_id,
                    partner=rec.vendor_id
                )
                untaxed += tax_data['total_excluded']
                taxes += tax_data['total_included'] - tax_data['total_excluded']

            rec.amount_untaxed = untaxed
            rec.amount_tax = taxes
            rec.amount_total = untaxed + taxes

    @api.model
    def create(self, vals):
        if not vals.get('pr_ref'):
            last_pr = self.search([], order='id desc', limit=1)
            next_number = 1
            if last_pr and last_pr.pr_ref:
                try:
                    last_num = int(last_pr.pr_ref.split('-')[-1])
                    next_number = last_num + 1
                except Exception:
                    pass
            vals['pr_ref'] = 'FSC-PR-' + str(next_number).zfill(4)
        return super().create(vals)


class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _description = 'Purchase Request Line'

    request_id = fields.Many2one('purchase.request', string="Purchase Request", ondelete='cascade')
    sequence = fields.Integer(string="Sequence", default=10)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")
    ], string="Display Type", help="Technical field for managing sections/notes.")
    product_id = fields.Many2one('product.product', string="Product", domain="[('purchase_ok', '=', True)]")
    name = fields.Text(string="Description")
    product_qty = fields.Float(string="Quantity", default=1.0)
    product_uom = fields.Many2one('uom.uom', string="Unit of Measure")
    price_unit = fields.Float(string="Unit Price with VAT")
    taxes_id = fields.Many2many('account.tax', string="Taxes",
                                domain="[('type_tax_use','=','purchase')]")
    price_subtotal = fields.Monetary(string="Subtotal", compute='_compute_subtotal', store=True)
    currency_id = fields.Many2one('res.currency', related='request_id.currency_id', store=True)
    company_id = fields.Many2one('res.company', related='request_id.company_id', store=True)

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.product_qty * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.name = line.product_id.display_name
                line.product_uom = line.product_id.uom_id.id
                line.price_unit = line.product_id.standard_price or 0.0
