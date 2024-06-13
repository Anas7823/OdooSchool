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

        carte_identite = files.get('carte_identite')
        carte_identite_data = carte_identite.read() if carte_identite else None
        carte_identite_name = carte_identite.filename if carte_identite else None
        _logger.info('Carte Identite: %s', carte_identite_name)

        justificatif_domicile = files.get('justificatif_domicile')
        justificatif_domicile_data = justificatif_domicile.read() if justificatif_domicile else None
        justificatif_domicile_name = justificatif_domicile.filename if justificatif_domicile else None
        _logger.info('Justificatif Domicile: %s', justificatif_domicile_name)

        certificat_medical = files.get('certificat_medical')
        certificat_medical_data = certificat_medical.read() if certificat_medical else None
        certificat_medical_name = certificat_medical.filename if certificat_medical else None
        _logger.info('Certificat Medical: %s', certificat_medical_name)

        # Convertir la date de naissance au format YYYY-MM-DD
        student_dob_str = kwargs.get('student_dob')
        student_dob = datetime.strptime(student_dob_str, '%d/%m/%Y').strftime('%Y-%m-%d') if student_dob_str else None
        
        # Créer un nouvel enregistrement d'étudiant avec les données du formulaire
        request.env['school.student'].sudo().create({
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
            'carte_identite': base64.b64encode(carte_identite_data) if carte_identite_data else None,
            'carte_identite_name': carte_identite_name,
            'justificatif_domicile': base64.b64encode(justificatif_domicile_data) if justificatif_domicile_data else None,
            'justificatif_domicile_name': justificatif_domicile_name,
            'certificat_medical': base64.b64encode(certificat_medical_data) if certificat_medical_data else None,
            'certificat_medical_name': certificat_medical_name,
            'droit_image': kwargs.get('droit_image'),
        })

        return request.redirect('/contactus-thank-you')
