# -*- coding: utf-8 -*-
{
    'name': "Custom Contract",

    'summary': """Calculate amount on invoice from .csv files""",

    'description': """
        Amount of some invoices need to be calculate from .csv files and based on packages

    """,

    'author': 'PK Consulting Services',
    'website': "http://pk067.herokuapp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Contract Management',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account_analytic_analysis'],

    # always loaded
    'data': [
        'views/contracts_view.xml',
        'data/scheduled_action_data.xml'
    ],
    'installable': True,
    'auto_install': False,

}