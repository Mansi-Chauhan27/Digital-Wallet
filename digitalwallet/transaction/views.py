from client.models import User
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
# from django.contrib.auth.models import User
from rest_framework import generics, serializers
from .models import CardDetails
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from client.decorators import admin_required, group_required
from rest_framework.authtoken.models import Token
from common.helper.utils import cardgen
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     print('queryset',queryset)
#     permission_classes = (AllowAny,)
#     serializer_class = RegisterSerializer

#     print(serializer_class.data)

   
# @csrf_exempt
# @api_view(["POST","GET"])
# @permission_classes((AllowAny,))
# @login_required
# # @admin_required
# # @group_required('admin')
# def generateCardNumber(request):

#     print('dwef')
#     print(request.user)
#     result={}
#     card_no = cardgen()
#     while  CardDetails.objects.filter(card_number=int(card_no)) :
#         card_no = cardgen()

#     print('request.data',request.data)
#     if card_no:
#         u = User.objects.get(id=request.data['id'])
#         card = CardDetails(user=u,card_number=card_no)
#         card.save()
#         print(card.card_number,'card_number')
#         result['msg'] = "Card Save Successfully"
#     else:
#         result['msg'] = "Error Generating Card"
#     return Response({'msg': 'Success','data':result},status=HTTP_200_OK)
#     # return Response({'msg': 'Success'},status=HTTP_200_OK)



class GenerateCardNumber(APIView):
    permission_classes = (IsAuthenticated,)
    print('sdafdas')

    @method_decorator(group_required('admin'))
    def post(request):
        print('dwef')
        print(request.user)
        result={}
        card_no = cardgen()
        while  CardDetails.objects.filter(card_number=int(card_no)) :
            card_no = cardgen()

        print('request.data',request.data)
        if card_no:
            u = User.objects.get(id=request.data['id'])
            card = CardDetails(user=u,card_number=card_no)
            card.save()
            print(card.card_number,'card_number')
            result['msg'] = "Card Save Successfully"
        else:
            result['msg'] = "Error Generating Card"
        return Response({'msg': 'Success','data':result},status=HTTP_200_OK)
        # return Response({'msg': 'Success'},status=HTTP_200_OK)

