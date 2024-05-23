from odoo import http
from odoo.http import request
from datetime import datetime
import base64

class StudentController(http.Controller):
    @http.route('/inscription', type='http', auth='public', website=True)
    def student_form(self, **kwargs):
        return http.request.render('school.web_form_newStudent', {})

    @http.route('/student/submit', type='http', auth='public', methods=['POST'], csrf=False)
    def submit_form(self, **kwargs):
        files = request.httprequest.files
        carte_identite = files.get('carte_identite')
        justificatif_domicile = files.get('justificatif_domicile')
        certificat_medical = files.get('certificat_medical')

        carte_identite_base64 = base64.b64encode(carte_identite.read()) if carte_identite else False
        justificatif_domicile_base64 = base64.b64encode(justificatif_domicile.read()) if justificatif_domicile else False
        certificat_medical_base64 = base64.b64encode(certificat_medical.read()) if certificat_medical else False

        # Convertir la date de naissance au format YYYY-MM-DD
        student_dob_str = kwargs.get('student_dob')
        student_dob = datetime.strptime(student_dob_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        
        # Créer un nouvel enregistrement d'étudiant avec les données du formulaire
        request.env['school.student'].sudo().create({
            'type_inscription': kwargs.get('type_inscription'),
            'name': kwargs.get('name'),
            'prenom': kwargs.get('prenom'),
            'student_dob': student_dob,
            'gender': kwargs.get('gender'),
            'num': kwargs.get('num'),
            'mail': kwargs.get('mail'),
            'adresse': kwargs.get('adresse'),
            'ville': kwargs.get('ville'),
            'code_postal': kwargs.get('code_postal'),
            'carte_identite': carte_identite_base64,
            'justificatif_domicile': justificatif_domicile_base64,
            'certificat_medical': certificat_medical_base64,
            'droit_image': kwargs.get('droit_image'),
        })

        return request.redirect('/contactus-thank-you')
