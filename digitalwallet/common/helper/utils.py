import random as r
from apps.transaction.models import Card
from apps.client.models import User


def otpgen():
    otp=""
    for i in range(4):
        otp+=str(r.randint(1,9))
    print ("Your One Time Password is ")
    print (otp)
    return otp

def cardgen():
    # print(request.user)
    card=""
    for i in range(16):
        card+=str(r.randint(1,9))
    return card


def generateCardNumber(userid,balance):
    print('dwef')
    print(userid)
    result={}
    card_no = cardgen()
    while  Card.objects.filter(card_number=int(card_no)) :
        card_no = cardgen()

    # print('request.data',request.data)
    # data = request.data['data']
    # print(data)
    if userid:
        u = User.objects.get(id=userid)
        card = Card(user=u,card_number=card_no,is_active=True,balance=balance)
        card.save()
        print(card.card_number,'card_number')
        result['msg'] = "Card Save Successfully"
        result['card_id'] = card.id
    else:
        result['msg'] = "Error Generating Card"

    return card.id
    # return Response({'msg': 'Success'},status=HTTP_200_OK)

