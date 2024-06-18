from odoo import http
from odoo.http import request
from datetime import datetime
import base64
import logging

_logger = logging.getLogger(__name__)

class StudentController(http.Controller):
    @http.route('/inscription', type='http', auth='public', website=True)
    def student_form(self, **kwargs):
        return http.request.render('school.web_form_newStudent', {})

    @http.route('/student/submit', type='http', auth='public', methods=['POST'], csrf=False)
    def submit_form(self, **kwargs):
        files = request.httprequest.files

        # Récupérer les fichiers uploadés
        fichier_carte_identite = files.get('carte_identite')
        justificatif_domicile = files.get('justificatif_domicile')
        certificat_medical = files.get('certificat_medical')

        # Log details about each file
        _logger.info('fichier_carte_identite: %s', fichier_carte_identite)
        _logger.info('justificatif_domicile: %s', justificatif_domicile)
        _logger.info('certificat_medical: %s', certificat_medical)

        attachments = {}
        
        # Create attachment for each file if present
        if fichier_carte_identite:
            attachments['carte_identite'] = request.env['ir.attachment'].sudo().create({
                'name': fichier_carte_identite.filename,
                'type': 'binary',
                'datas': base64.b64encode(fichier_carte_identite.read()),
                'res_model': 'school.student',
                'res_id': 0,
            })

        if justificatif_domicile:
            attachments['justificatif_domicile'] = request.env['ir.attachment'].sudo().create({
                'name': justificatif_domicile.filename,
                'type': 'binary',
                'datas': base64.b64encode(justificatif_domicile.read()),
                'res_model': 'school.student',
                'res_id': 0,
            })

        if certificat_medical:
            attachments['certificat_medical'] = request.env['ir.attachment'].sudo().create({
                'name': certificat_medical.filename,
                'type': 'binary',
                'datas': base64.b64encode(certificat_medical.read()),
                'res_model': 'school.student',
                'res_id': 0,
            })

        # Log information about the attachments
        _logger.info('Attachment carte_identite: %s', attachments.get('carte_identite'))
        _logger.info('Attachment justificatif_domicile: %s', attachments.get('justificatif_domicile'))
        _logger.info('Attachment certificat_medical: %s', attachments.get('certificat_medical'))

        # Convertir la date de naissance au format YYYY-MM-DD
        student_dob_str = kwargs.get('student_dob')
        student_dob = datetime.strptime(student_dob_str, '%d/%m/%Y').strftime('%Y-%m-%d') if student_dob_str else None
        
        # Créer un nouvel enregistrement d'étudiant avec les données du formulaire
        student = request.env['school.student'].sudo().create({
            'type_inscription': kwargs.get('type_inscription'),
            'name': kwargs.get('name'),
            'prenom': kwargs.get('prenom'),
            'student_dob': student_dob,
            'nom_tuteur': kwargs.get('nom_tuteur'),
            'prenom_tuteur': kwargs.get('prenom_tuteur'),
            'num_tuteur': kwargs.get('num_tuteur'),
            'mail_tuteur': kwargs.get('mail_tuteur'),
            'gender': kwargs.get('gender'),
            'num': kwargs.get('num'),
            'mail': kwargs.get('mail'),
            'adresse': kwargs.get('adresse'),
            'ville': kwargs.get('ville'),
            'code_postal': kwargs.get('code_postal'),
            'carte_identite': attachments.get('carte_identite').datas if attachments.get('carte_identite') else None,
            'carte_identite_name': attachments.get('carte_identite').name if attachments.get('carte_identite') else None,
            'justificatif_domicile': attachments.get('justificatif_domicile').datas if attachments.get('justificatif_domicile') else None,
            'justificatif_domicile_name': attachments.get('justificatif_domicile').name if attachments.get('justificatif_domicile') else None,
            'certificat_medical': attachments.get('certificat_medical').datas if attachments.get('certificat_medical') else None,
            'certificat_medical_name': attachments.get('certificat_medical').name if attachments.get('certificat_medical') else None,
            'droit_image': kwargs.get('droit_image'),
        })

        # Mettre à jour les res_id des attachments pour qu'ils pointent vers le nouvel étudiant créé
        for attachment in attachments.values():
            attachment.write({'res_id': student.id})

        # Rediriger l'utilisateur vers la page de remerciement
        return request.redirect('/contactus-thank-you')
