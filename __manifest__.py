# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Club manager',
    'summary': 'Formulaire en code',
    'description': """
        Ce module permet de générer une page de formulaire d\'inscription pour votre club de foot. 
        Il permet de gérer les inscriptions des joueurs et les paiements.
    """,
    'category': 'Tools',
    'author': 'Start zup',
    'maintainer': "",
    'company': 'Start zup',
    'website': 'https://start-zup.com/',
    'license': 'AGPL-3',
    'depends': ['base', 'mail', 'sale_management', 'website', 'payment_stripe'],
    'data': [
        'security/ir.model.access.csv',
        # 'views/sale_order_view.xml',
        'views/student_view.xml',
        'views/newStudent.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

