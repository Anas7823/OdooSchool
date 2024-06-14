from odoo import api, fields, models

from datetime import datetime
from dateutil.relativedelta import relativedelta
# import stripe
from odoo.exceptions import UserError

class Student(models.Model):
    # the model name (in dot-notation, module namespace)
    _name = 'school.student'
    # python-inherited modelsStudent
    _inherit = ['mail.thread']
    # the model's informal name
    _description = ' Record'
    # default order field for searching results
    _order = 'name'

    def button_done(self):
        for rec in self:
            rec.write({'state': 'done'})

    def button_reset(self):
        for rec in self:
            rec.state = 'reset'


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
    
    #si réinscription on demande l'ancienne licence
    old_licence = fields.Image(string='Ancienne licence')
    old_num_licence = fields.Char(string='Numéro de licence')
    # fin: si réinscription
    name = fields.Char(string='Nom', required=True)
    prenom = fields.Char(string='Prénom', required=True)
    photo = fields.Binary(string='Image')
    student_dob = fields.Date(string="Date de naissance")
    gender = fields.Selection(
        [('homme', 'Homme'), ('femme', 'Femme')],
        string='Gender')
    # si n'ai pas majeur on demande les informations du tuteur
    nom_tuteur = fields.Char(string='Nom du tuteur')
    prenom_tuteur = fields.Char(string='Prénom du tuteur')
    num_tuteur = fields.Char(string='Numéro du tuteur')
    mail_tuteur = fields.Char(string='Mail du tuteur')
    # fin : si n'ai pas majeur
    # si majeur on demande les informations personnelles du joueur
    num = fields.Char(string='Numéro de téléphone')
    mail = fields.Char(string='Mail')
    # fin : si majeur
    adresse = fields.Text(string='Adresse')
    ville = fields.Char(string='Ville')
    code_postal = fields.Char(string='Code Postal')
    carte_identite = fields.Binary(string='Carte d\'identité', attachment=True)
    carte_identite_name = fields.Char(string='Nom de la carte d\'identité')
    # carte_identite_ids = fields.Many2many('ir.attachment', string='Carte d\'identité')
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

    @api.depends('student_dob')
    def _compute_is_major(self):
        for student in self:
            if student.student_dob:
                # Calculer l'age en années
                age_years = (fields.Date.today() - student.student_dob).days / 365.25
                student.is_major = age_years >= 18
            else:
                student.is_major = False
                
    @api.depends('student_dob')  
    def _compute_age(self):
        for student in self:
            if student.student_dob:
                # Calculer l'age en années
                student.age = (fields.Date.today() - student.student_dob).days / 365.25
            else:
                student.age = 0

    # On déclare un montant pour la licence
    # amount = fields.Float(string="Montant", default=270.0)
    # reste_a_payer = fields.Float(string="Reste à payer", compute='_compute_reste_a_payer', store=True)
    
    # Fonction qui automatise le calcul du montant restant à payer
    # @api.depends('amount', 'paiement_montant')
    # def _compute_reste_a_payer(self):
    #     for student in self:
    #         student.reste_a_payer = student.amount - student.paiement_montant

    # On crée une méthode pour générer le lien de paiement Stripe
    # @api.multi
    # def action_generate_stripe_link(self):
    #     self.ensure_one()
    #     stripe.api_key = 'sk_test_51O7E1CAJayP49dnd7leDgQCPz9PrkxnQoCPBufUow0NGdkmQYpvPBcePgS9w7D9mO3QNKSr6fSTB9u0HKwY2sYcs00igPdWbqL'

    #     try:
    #         # Crée un lien de paiement Stripe
    #         checkout_session = stripe.checkout.Session.create(
    #             payment_method_types=['card'],
    #             line_items=[{
    #                 'price_data': {
    #                     'currency': 'eur', 
    #                     'product_data': {
    #                         'name': 'Licence de football estrappes',
    #                     },
    #                     'unit_amount': int(self.amount * 100), # Convertir le montant en centimes
    #                 },
    #                 'quantity': 1,
    #             }],
    #             mode='payment',
    #             success_url='http://localhost:8069/contactus-thank-you',
    #             cancel_url='http://localhost:8069/',
    #         )
            
    #         # Envoyer l'email avec le lien de paiement
    #         mail_template = self.env.ref('school.email_template_stripe_payment')
    #         mail_template.sudo().with_context(
    #             stripe_payment_url=checkout_session.url
    #         ).send_mail(self.id, force_send=True)
            
    #     except Exception as e:
    #         raise UserError(f"Erreur lors de la création du lien de paiement Stripe : {str(e)}")
        