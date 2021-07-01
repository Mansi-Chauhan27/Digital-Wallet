import random as r

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
    for i in range(12):
        card+=str(r.randint(1,9))
    return card