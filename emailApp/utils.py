import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.mail import EmailMessage


logger=logging.getLogger(__name__)

def send_email_with_html_body(subjet:str,receivers:list,template:str,context:dict):
    """ This function help to send a customize email to a specific user or set of users."""

    try:
        message=render_to_string(template,context)
        send_mail(
            subjet,
            message,
            settings.EMAIL_HOST_USER,
            receivers,
            fail_silently=True,
            html_message=message
        )
        return True

    except Exception as e:
        logger.error(e)
    return False




def send_email_with_html_body2(subject:str, receivers:list, template:str, context:dict, attachment_path:str=""):
    """ This function helps to send a customized email to a specific user or set of users with an attachment."""

    try:
        # Rendre le message HTML à partir du template
        html_message = render_to_string(template, context)
        
        # Créer l'objet EmailMessage
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=receivers
        )
        
        # Ajouter le contenu HTML
        email.content_subtype = 'html'
        
        # Ouvrir le fichier image en mode binaire et l'attacher
        with open(attachment_path, 'rb') as img:
            email.attach(filename='image.jpg', content=img.read(), mimetype='image/jpeg')
        
        # Envoyer l'email
        email.send()
        return True

    except Exception as e:
        logger.error(e)
        return False



def send_email_with_html_body3(subject:str, receivers:list, template:str, context:dict):
    """ This function helps to send a customized email to a specific user or set of users with an attachment."""

    try:
        # Rendre le message HTML à partir du template
        html_message = render_to_string(template, context)
        
        # Créer l'objet EmailMessage
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=receivers
        )
        
        # Ajouter le contenu HTML
        email.content_subtype = 'html'
        
        
        # Envoyer l'email
        email.send()
        return True

    except Exception as e:
        logger.error(e)
        return False
