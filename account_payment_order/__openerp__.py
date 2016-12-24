# -*- coding: utf-8 -*-
{
    'name': "Account Payment Order",

    'summary': """
    This module create account payment order. You can post, set to draft state, can delete or cancel it. 
    account.payment.order
        """,

    'description': """
        Account payment order module.         
    """,

    'author': "Shahid Mehmood",
    'website': "shahid.ibex@yahoo.com",
    'category': 'Accounting &amp; Finance',
    'version': '0.1',
    'depends': ['base','payment','account', 'account_accountant', 'account_payment_order_report'],

    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'views/account_payment_order_sequence.xml',
        'views/account_payment_order_view.xml',
    ],
    'demo': [
        'demo_data.xml',
    ],
}