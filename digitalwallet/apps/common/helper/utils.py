import random as r

# from apps.clients.models import User


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



import cgi
from datetime import datetime, timedelta
from io import \
    BytesIO  # A stream implementation using an in-memory bytes buffer It inherits BufferIOBase
from io import StringIO
from tempfile import NamedTemporaryFile

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

#pisa is a html2pdf converter using the ReportLab Toolkit,
#the HTML5lib and pyPdf.
 
#difine render_to_pdf() function

 
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
    result_file.close()               

    print('testtttt',pisa_status.err)

     
    # print(pdf)
    if not pisa_status.err:
        return 'Success'
    #  return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
 

def is_leap_year(year): 
    if (year % 4) == 0: 
        if (year % 100) == 0: 
            if (year % 400) == 0: 
                return True
            else: 
                return False
        else: 
             return True
    else: 
        return False

def get_lapse():
    last_month = datetime.today().month - 1 
    if(last_month==1):
        last_month=12
    print(last_month)
    current_year = datetime.today().year

    #is last month a month with 30 days?
    if last_month in [9, 4, 6, 11]:
        lapse = 30

    #is last month a month with 31 days?
    elif last_month in [1, 3, 5, 7, 8, 10, 12]:
        lapse = 31

    #is last month February?
    else:
        if is_leap_year(current_year):
            lapse = 29
        else:
            lapse = 30
    print(lapse)
    return lapse


get_lapse()
