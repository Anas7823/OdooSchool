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
        # Récupérer les fichiers uploadés
        files = request.httprequest.files

        # Log details about each file
        _logger.info('Uploaded files: %s', files)

        attachments = {}

        # Process each file and create attachments
        for field_name, file_list in files.lists():
            for index, file_value in enumerate(file_list):
                if file_value.filename:
                    attachment_data = {
                        'name': file_value.filename,
                        'type': 'binary',
                        'datas': base64.b64encode(file_value.read()),
                        'res_model': 'school.student',
                        'res_id': 0,  # Initially set to 0, will be updated after student creation
                    }
                    attachments[field_name] = request.env['ir.attachment'].sudo().create(attachment_data)

        # Log information about the created attachments
        _logger.info('Created attachments: %s', attachments)

        # Convertir la date de naissance au format YYYY-MM-DD
        student_dob_str = kwargs.get('student_dob')
        student_dob = datetime.strptime(student_dob_str, '%d/%m/%Y').strftime('%Y-%m-%d') if student_dob_str else None
        
        # Créer un nouvel enregistrement d'étudiant avec les données du formulaire
        student_data = {
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
            'droit_image': kwargs.get('droit_image'),
        }

        # Create the student record first
        student = request.env['school.student'].sudo().create(student_data)

        # Update res_id of attachments to point to the newly created student
        for field_name, attachment in attachments.items():
            attachment.write({'res_id': student.id})

            # Map the attachment to the correct field
            if 'carte_identite' in field_name:
                student.write({'carte_identite': attachment.id})
            elif 'justificatif_domicile' in field_name:
                student.write({'justificatif_domicile': attachment.id})
            elif 'certificat_medical' in field_name:
                student.write({'certificat_medical': attachment.id})

        # Log information about the created student
        _logger.info('Created student: %s', student)

        # Redirect to a success page or return a response
        return http.request.redirect('/contactus-thank-you')
