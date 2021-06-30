from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def sendEmailForVerification(otp,receiver_email):
    
    # SENDER_EMAIL = conf_settings.ADMIN_ID
    SENDER_EMAIL = 'mfsi.mansic@gmail.com'
    print('SENDER_EMAIL',SENDER_EMAIL)
    RECEIVER_EMAIL = ['mansichauhan15@gmail.com']
    
    SUBJECT='Email Verification'

    
    if(RECEIVER_EMAIL):
        try:
            for item in RECEIVER_EMAIL :
                print(item)
                HTML = """
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8" />
                </head>
                <body>
                    Hi your otp is ,<br> <br>
                    """+str(otp)+"""
                    <br><br>
                    
                    <br>
                    <br>
                    Thank you!
                </body>
                </html>
                """
            
                message1 = Mail(from_email=SENDER_EMAIL,to_emails=str(item),subject=SUBJECT,html_content=HTML)
            
                sg = SendGridAPIClient('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')
                response = sg.send(message1)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            # return response
        except Exception as e:
            print(e)
            # data = {'error':'1'}
            # return data



sendEmailForVerification(2334,'mansichauhan15@gmail.com')