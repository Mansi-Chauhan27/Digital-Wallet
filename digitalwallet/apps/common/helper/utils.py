import random as r
from apps.transactions.models import Card
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


def generateCardNumber(userid,balance):
    result={}
    card_no = cardgen()
    while  Card.objects.filter(card_number=int(card_no)) :
        card_no = cardgen()

    if userid:
        u = User.objects.get(id=userid)
        card = Card(user=u,card_number=card_no,is_active=True,balance=balance)
        card.save()
        result['msg'] = "Card Save Successfully"
        result['card_id'] = card.id
    else:
        result['msg'] = "Error Generating Card"

    return card.id
    # return Response({'msg': 'Success'},status=HTTP_200_OK)

