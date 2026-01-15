# -*- coding: utf-8 -*-
# from odoo import http


# class CustomJournalReporting(http.Controller):
#     @http.route('/custom_journal_reporting/custom_journal_reporting', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_journal_reporting/custom_journal_reporting/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_journal_reporting.listing', {
#             'root': '/custom_journal_reporting/custom_journal_reporting',
#             'objects': http.request.env['custom_journal_reporting.custom_journal_reporting'].search([]),
#         })

#     @http.route('/custom_journal_reporting/custom_journal_reporting/objects/<model("custom_journal_reporting.custom_journal_reporting"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_journal_reporting.object', {
#             'object': obj
#         })

