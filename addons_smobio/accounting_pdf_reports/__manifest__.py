# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo 13 Accounting PDF Reports',
    'version': '13.0.1.0.2',
    'category': 'Invoicing Management',
    'summary': 'Accounting Reports For Odoo 13',
    'sequence': '10',
    'author': 'Odoo Mates, Odoo SA',
    'license': 'LGPL-3',
    'company': 'Odoo Mates',
    'maintainer': 'Odoo Mates',
    'support': 'odoomates@gmail.com',
    'website': '',
    'depends': ['account'],
    'live_test_url': 'https://www.youtube.com/watch?v=Qu6R3yNKR60',
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/account_pdf_reports.xml',
        'views/account_reports_settings.xml',
        'wizards/partner_ledger.xml',
        'wizards/general_ledger.xml',
        #'wizards/trial_balance.xml',
        'wizards/balance_sheet.xml',
        'wizards/profit_and_loss.xml',
        #'wizards/tax_report.xml',
        'wizards/aged_partner.xml',
        'wizards/journal_audit.xml',
        # 'wizards/cash_flow_statement.xml',
        'reports/report.xml',
        'reports/report_partner_ledger.xml',
        'reports/report_general_ledger.xml',
        'reports/report_trial_balance.xml',
        'reports/report_financial.xml',
        'reports/report_tax.xml',
        'reports/report_aged_partner.xml',
        'reports/report_journal_audit.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'qweb': [],
}
