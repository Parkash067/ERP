# -*- coding: utf-8 -*-
{
    'name': "Custom HR",

    'summary': """Calculate commissions based on opportunities and sales per week """,

    'description': """
        Generate salary slip including commisions of an employee

    """,

    'author': 'PK Consulting Services',
    'website': "http://pk067.herokuapp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'HR',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','hr'],

    # always loaded
    'data': [
        'views/hr_view.xml',
        'data/scheduled_action_data.xml'
    ],
    'installable': True,
    'auto_install': False,

}