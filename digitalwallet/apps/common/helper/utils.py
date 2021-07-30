import random as r
# from apps.transactions.models import Card
from apps.clients.models import User


def otpgen():
    otp=""
    for i in range(4):
        otp+=str(r.randint(1,9))
    return otp

def cardgen():
    card=""
    for i in range(16):
        card+=str(r.randint(1,9))
    return card


# def generateCardNumber(userid,balance):
#     result={}
#     card_no = cardgen()
#     while  Card.objects.filter(card_number=int(card_no)) :
#         card_no = cardgen()

#     if userid:
#         u = User.objects.get(id=userid)
#         card = Card(user=u,card_number=card_no,is_active=True,balance=balance)
#         card.save()
#         result['msg'] = "Card Save Successfully"
#         result['card_id'] = card.id
#     else:
#         result['msg'] = "Error Generating Card"

#     return card.id
#     # return Response({'msg': 'Success'},status=HTTP_200_OK)

from io import BytesIO #A stream implementation using an in-memory bytes buffer
                       # It inherits BufferIOBase
 
from django.http import HttpResponse
from django.template.loader import get_template
 
#pisa is a html2pdf converter using the ReportLab Toolkit,
#the HTML5lib and pyPdf.
 
from xhtml2pdf import pisa  
#difine render_to_pdf() function

from io import StringIO
import cgi
 
def render_to_pdf(template_src, filename, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
 
    #This part will create the pdf.
    # pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)

    # open output file for writing (truncated binary)
    result_file = open('pdf/'+filename, "w+b")

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
            html,                # the HTML to convert
            dest=result_file)           # file handle to recieve result

    # close output file
    result_file.close()                 # close output file

                # close output file
    print('testtttt',pisa_status.err)

     
    # print(pdf)
    if not pisa_status.err:
        return 'Success'
    #  return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
 