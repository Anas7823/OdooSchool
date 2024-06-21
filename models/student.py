from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
import sys
import logging

_logger = logging.getLogger(__name__)

_logger.info("Python path: %s", sys.path)

try:
    import stripe    
    _logger.error("Stripe a été installer avec succès.")
except ImportError:
    _logger.error("Stripe module not found. Please make sure it is installed and the environment is activated.")


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
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments', domain="[('res_model', '=', 'school.student'), ('res_id', '=', id)]")
    # Champs pour les pièces jointes
    carte_identite = fields.Many2one('ir.attachment', string='Carte d\'identité')
    justificatif_domicile = fields.Many2one('ir.attachment', string='Justificatif de domicile')
    certificat_medical = fields.Many2one('ir.attachment', string='Certificat médical')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', string='Documents', domain=[('res_model', '=', 'school.student')])
    
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
        
    stripe_payment_link = fields.Char(string='Lien de paiement Stripe')
    
    def action_generate_payment_link(self):
        self.write({'status': 'attente'})
        for record in self:
            try:
                # Configurez votre clé API Stripe
                stripe.api_key = 'sk_test_51O7E1CAJayP49dnd7leDgQCPz9PrkxnQoCPBufUow0NGdkmQYpvPBcePgS9w7D9mO3QNKSr6fSTB9u0HKwY2sYcs00igPdWbqL'

                # Créez un objet Price
                price = stripe.Price.create(
                    unit_amount=27000, # Montant en centime (270€)
                    currency='eur',
                    product_data={
                        'name': 'Licence de football',
                    },
                )
                
                # Créez un lien de paiement
                payment_link = stripe.PaymentLink.create(
                    line_items=[
                        {
                            'price': price.id,
                            'quantity': 1,
                        },
                    ],
                )

                # Stockez le lien de paiement dans l'enregistrement de l'étudiant
                record.stripe_payment_link = payment_link.url

                # Envoyez un email avec le lien de paiement
                template_id = self.env.ref('school.email_template_payment_link').id
                template = self.env['mail.template'].browse(template_id)
                template.send_mail(record.id, force_send=True)
                
                _logger.info("Payment link generated and email sent for student: %s", record.name)

            except stripe.error.StripeError as e:
                _logger.error("Stripe error: %s", e)
