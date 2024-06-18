import sys
# sys.path.append("../../server/odoo/addons")
# sys.path.append("../venv/Lib/site-packages/stripe")
from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
# import stripe
import logging

_logger = logging.getLogger(__name__)

class Student(models.Model):
    _name = 'school.student'
    _inherit = ['mail.thread']
    _description = 'Record'
    _order = 'name'

    status = fields.Selection([
        ('refus', 'Refus'),
        ('new', 'New'),
        ('attente', 'Attente de paiement'),
        ('done', 'Done'),
    ], string='Status', default='new')

    type_inscription = fields.Selection([
        ('new', 'Nouvelle inscription'),
        ('renouvellement', 'Renouvellement'),
        ('mutation', 'Mutation')
    ], string='Type d\'inscription', default='new')

    old_licence = fields.Image(string='Ancienne licence')
    old_num_licence = fields.Char(string='Numéro de licence')
    name = fields.Char(string='Nom', required=True)
    prenom = fields.Char(string='Prénom', required=True)
    photo = fields.Binary(string='Image')
    student_dob = fields.Date(string="Date de naissance")
    gender = fields.Selection(
        [('homme', 'Homme'), ('femme', 'Femme')],
        string='Gender')

    nom_tuteur = fields.Char(string='Nom du tuteur')
    prenom_tuteur = fields.Char(string='Prénom du tuteur')
    num_tuteur = fields.Char(string='Numéro du tuteur')
    mail_tuteur = fields.Char(string='Mail du tuteur')

    num = fields.Char(string='Numéro de téléphone')
    mail = fields.Char(string='Mail')

    adresse = fields.Text(string='Adresse')
    ville = fields.Char(string='Ville')
    code_postal = fields.Char(string='Code Postal')
    carte_identite = fields.Binary(string='Carte d\'identité', attachment=True)
    carte_identite_name = fields.Char(string='Nom de la carte d\'identité')
    justificatif_domicile = fields.Binary(string='Justificatif de domicile', attachment=True)
    justificatif_domicile_name = fields.Char(string='Nom du justificatif de domicile')
    certificat_medical = fields.Binary(string='Certificat médical', attachment=True)
    certificat_medical_name = fields.Char(string='Nom du certificat médical')
    droit_image = fields.Selection([
        ('oui', 'J\'accepte que le club utilise mon image sur toutes ses plateformes.'),
        ('non', 'Je refuse que le club utilise mon image.')
    ], string='Droit à l\'image')

    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    
    paiement = fields.Selection([
        ('cheque', 'Chèque'),
        ('virement', 'Virement'),
        ('especes', 'Espèces')
    ], string='Moyen de paiement')
    paiement_date = fields.Date(string='Date de paiement')
    paiement_montant = fields.Float(string='Montant payé')

    etat_pack_licence = fields.Selection([
        ('obtenue', 'Pack acheté'),
        ('non_obtenue', 'Pack non acheté')
    ], string='Pack licencié', default='non_obtenue')

    partner_id = fields.Many2one('res.partner', string='Partenaire')

    @api.depends('student_dob')
    def _compute_age(self):
        for student in self:
            if student.student_dob:
                student.age = (fields.Date.today() - student.student_dob).days // 365
            else:
                student.age = 0

    def button_done(self):
        self.write({'status': 'done'})

    def button_reset(self):
        self.write({'status': 'reset'})

    def action_paiement_state(self):
        self.write({'status': 'attente'})

    def action_done_state(self):
        self.write({'status': 'done'})

    def button_cancel(self):
        self.write({'status': 'refus'})

    def delete_record(self):
        self.unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # def generate_payment_link(self):
    #     product_id = 35  # Remplacez par l'ID correct de votre produit dans Odoo

    #     # Vérifier que l'étudiant n'a pas déjà payé
    #     if self.paiement_date:
    #         raise UserError("This student has already paid.")

    #     # Créer la vente d'une licence à 270€
    #     product_template = self.env['product.template'].browse(product_id)
    #     if not product_template:
    #         raise UserError("License product not found. Please configure it.")

    #     product = self.env['product.product'].search([('product_tmpl_id', '=', product_id)], limit=1)
    #     if not product:
    #         raise UserError("Product variant not found. Please configure it.")

    #     # Si l'étudiant n'a pas de partenaire associé, créer un nouveau partenaire
    #     if not self.partner_id:
    #         partner_vals = {
    #             'name': f"{self.prenom} {self.name}",
    #             'phone': self.num,
    #             'email': self.mail,
    #             'street': self.adresse,
    #             'city': self.ville,
    #             'zip': self.code_postal,
    #         }
    #         self.partner_id = self.env['res.partner'].create(partner_vals)

    #     # Créer la commande de vente
    #     sale_order = self.env['sale.order'].create({
    #         'partner_id': self.partner_id.id,
    #         'order_line': [(0, 0, {
    #             'product_id': product.id,
    #             'name': product.name,
    #             'product_uom_qty': 1,
    #             'price_unit': 270,
    #         })],
    #     })

    #     # Configure Stripe API
    #     stripe.api_key = "sk_test_51O7E1CAJayP49dnd7leDgQCPz9PrkxnQoCPBufUow0NGdkmQYpvPBcePgS9w7D9mO3QNKSr6fSTB9u0HKwY2sYcs00igPdWbqL"  # Remplacez par votre clé API Stripe

    #     # Create Stripe Checkout Session
    #     session = stripe.checkout.Session.create(
    #         payment_method_types=['card'],
    #         line_items=[{
    #             'price_data': {
    #                 'currency': 'eur',
    #                 'product_data': {
    #                     'name': product.name,
    #                 },
    #                 'unit_amount': 27000,  # 270 euros in cents
    #             },
    #             'quantity': 1,
    #         }],
    #         mode='payment',
    #         success_url='https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}',
    #         cancel_url='https://yourdomain.com/cancel',
    #     )

    #     # Get the payment link
    #     payment_link = session.url

    #     # Envoyer un e-mail à l'étudiant avec le lien de paiement
    #     template = self.env.ref('school.email_template_data')  # Remplacez par l'ID correct de votre modèle d'email
    #     if template:
    #         template.with_context(payment_url=payment_link).send_mail(self.id, force_send=True)

    #     # Mettre à jour le statut de paiement de l'étudiant
    #     self.write({
    #         'paiement': 'attente',
    #         'paiement_date': fields.Date.today(),
    #         'paiement_montant': 270,
    #     })

    #     return payment_link
