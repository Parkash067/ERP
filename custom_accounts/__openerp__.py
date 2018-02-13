#This file basically a definition of module i.e this file provides complete details of modules.
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Accounts and Financial Management',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 15,
    'author':'PK Consulting Services',
    'summary': 'Invoicing',
    'description': """
    Enable an email option on an invoice""",
    'website': 'http://pk067.herokuapp.com/',
    'depends': ['base_setup','account_accountant'],
    'data': ['views/invoice_view.xml','views/custom_invoice.xml','views/report_menu.xml'],
    'installable': True,
    'auto_install': False,

}