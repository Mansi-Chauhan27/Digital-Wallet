from django.conf import settings as conf_settings
import os
# from config.settings import SENDER_EMAIL
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import html
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# import django
# django.setup()
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def sendEmailForVerification(otp,receiver_email):
    DJANGO_SETTINGS_MODULE= conf_settings
    
    
    # SENDER_EMAIL = settings.ADMIN_ID
    SENDER_EMAIL = 'mfsi.mansic@gmail.com'
    RECEIVER_EMAIL = ['mansichauhan15@gmail.com']
    
    SUBJECT='Email Verification'

    
    if(RECEIVER_EMAIL):
        print('sfs')
        try:
            for item in RECEIVER_EMAIL :
                print('x')
                
                html_content = render_to_string('t.html', {'varname':'value'}) # render with dynamic value
                text_content = strip_tags(html_content) # Strip the html tag. So people can see the pure text at least.
                print(text_content)
                message1 = Mail(from_email=SENDER_EMAIL,to_emails=str(item),subject=SUBJECT,html_content=HTML)
            
                sg = SendGridAPIClient('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')
                response = sg.send(message1)
                print(response)
            # return response
        except Exception as e:
            print(e)
            pass
            # data = {'error':'1'}
            # return data

sendEmailForVerification(1212,'m')