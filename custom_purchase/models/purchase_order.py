# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # --------------------------
    # Vendor Information
    # --------------------------
    vendor_no = fields.Char(string="Vendor No")
    vendor_contact = fields.Char(string="Vendor Contact")
    vendor_phone = fields.Char(string="Vendor Phone", related='partner_id.phone', readonly=True)
    vendor_email = fields.Char(string="Vendor Email", related='partner_id.email', readonly=True)
    vendor_address_display = fields.Html(string="Vendor Address", compute="_compute_vendor_address_display")

    def _compute_vendor_address_display(self):
        for record in self:
            partner = record.partner_id
            record.vendor_address_display = partner._display_address(without_company=True) if partner else ""

    # --------------------------
    # Shipping Details (Employee-based)
    # --------------------------
    ship_employee_id = fields.Many2one(
        'hr.employee',
        string="Shipping Employee",
        help="Employee responsible for shipping",
        ondelete="set null"
    )
    ship_phone = fields.Char(string="Ship Phone", compute="_compute_ship_info", store=True)
    ship_email = fields.Char(string="Ship Email", compute="_compute_ship_info", store=True)
    ship_to = fields.Many2one('res.company', string="Ship To", default=lambda self: self.env.company)
    ship_address_display = fields.Html(string="Shipping Address", compute="_compute_ship_address_display")

    @api.depends('ship_employee_id')
    def _compute_ship_info(self):
        for rec in self:
            emp = rec.ship_employee_id
            rec.ship_phone = emp.work_phone if emp else ""
            rec.ship_email = emp.work_email if emp else ""

    def _compute_ship_address_display(self):
        for record in self:
            company = record.ship_to
            record.ship_address_display = (
                company.partner_id._display_address(without_company=True) if company else ""
            )

    # --------------------------
    # Billing Details (Employee-based)
    # --------------------------
    bill_employee_id = fields.Many2one(
        'hr.employee',
        string="Billing Employee",
        help="Employee responsible for billing",
        ondelete="set null"
    )
    bill_phone = fields.Char(string="Bill Phone", compute="_compute_bill_info", store=True)
    bill_email = fields.Char(string="Bill Email", compute="_compute_bill_info", store=True)
    bill_to = fields.Many2one('res.company', string="Bill To", default=lambda self: self.env.company)
    bill_address_display = fields.Html(string="Billing Address", compute="_compute_bill_address_display")

    @api.depends('bill_employee_id')
    def _compute_bill_info(self):
        for rec in self:
            emp = rec.bill_employee_id
            rec.bill_phone = emp.work_phone if emp else ""
            rec.bill_email = emp.work_email if emp else ""

    def _compute_bill_address_display(self):
        for record in self:
            company = record.bill_to
            record.bill_address_display = (
                company.partner_id._display_address(without_company=True) if company else ""
            )
