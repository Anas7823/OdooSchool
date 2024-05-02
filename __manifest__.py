# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'school',
    'summary': 'Formulaire en code',
    'description': '',
    'category': 'Tools',
    'author': 'aaa',
    'maintainer': "",
    'company': '',
    'website': '',
    'license': 'AGPL-3',
    'depends': ['base', 'mail', 'sale_management', 'website', 'payment_stripe'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/student_view.xml',
        'views/newStudent.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

