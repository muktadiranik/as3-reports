from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings

from as3.core.models.base import Users

def send_welcome_email(user:Users):
    if user.idCountry.name == "MX":
        email_template_name = "accounts/email/[es]Welcome-Mail.html"
        subject = "Termina de crear tu cuenta!"
    else:
        email_template_name = "accounts/email/[en]Welcome-Mail.html"
        subject = "Finish setting up your account!"
        
    c = {
        "email":user.email,
        'domain':settings.DOMAIN,
        'site_name': 'as3international',
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "user": user,
        'token': default_token_generator.make_token(user),
        'protocol': 'http',
    }
    user.send_email(
        subject = subject,
        html_content = render_to_string(email_template_name, c),
        to_emails= user.email,
    )