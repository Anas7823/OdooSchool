from odoo import http
from odoo.http import request
from datetime import datetime

class StudentController(http.Controller):
    @http.route('/inscription', type='http', auth='public', website=True)
    def student_form(self, **kwargs):
        return http.request.render('school.web_form_newStudent', {})

    @http.route('/student/submit', type='http', auth='public', methods=['POST'], csrf=False)
    def submit_form(self, **kwargs):
        # Convertir la date de naissance au format YYYY-MM-DD
        student_dob_str = kwargs.get('student_dob')
        student_dob = datetime.strptime(student_dob_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        # Créer un nouvel enregistrement d'étudiant avec les données du formulaire
        request.env['school.student'].sudo().create({
            'name': kwargs.get('name'),
            'prenom': kwargs.get('prenom'),
            'student_dob': student_dob,
            'gender': kwargs.get('gender'),
            'num': kwargs.get('num'),
            'mail': kwargs.get('mail'),
            'adresse': kwargs.get('adresse'),
            'ville': kwargs.get('ville'),
            'code_postal': kwargs.get('code_postal'),
            'carte_identite': kwargs.get('carte_identite'),
            'justificatif_domicile': kwargs.get('justificatif_domicile'),
            'certificat_medical': kwargs.get('certificat_medical'),
            'droit_image': kwargs.get('droit_image'),
        })
        return request.redirect('/thank_you')
