# -*- coding: utf-8 -*-
{
    'name': "Account Payment Order Report",

    'summary': """
       Account Payment Order Report of odoo v8.""",

    'description': """
Account Payment Order Report
=============================
    """,

    'author': "Shahid Mehmood",
    'website': "shahid.ibex@yahoo.com",
    'category': 'Accounting',
    'version': '1.0',
    'depends': ['base','account'],
    'data': [
        'views/report_account_payment_order.xml',
        #'views/report_external_layout_header.xml',
        #'views/report_external_layout_footer.xml',
        'account_payment_order_report.xml',
    ],

    'demo': [
    ],

    'tests': [
    ],
}
