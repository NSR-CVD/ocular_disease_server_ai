from Utilities.errorCode import internalErr


def isEmpty(value):
    isValue = False
    if value is None or value == "" or value == " ":
        isValue = True
    return isValue

def isString(value):
    if type(value) == str:
        return True
    else:
       return False

def isInt(value):
    if type(value) == int:
        return True
    else:
       return False
    
def ExceptionError(message, errorCase, code):
    Errors = {
        "error": {
            "code": message['code'],
            "messageTh": message['messageTh'],
            "messageEng": message['messageEng'],
            "errorCase": errorCase,
        },
        "statusCode" : code
    }
    return Errors

def exToResponse(error):
    try:
        response = {
            "error": {
            "code": internalErr['code'],
            "messageTh": internalErr['messageTh'],
            "messageEng": internalErr['messageEng'],
            "errorCase": error,
        },
            "statusCode" : 500
        } 
        return response["error"],response['statusCode']

    except Exception as error:
        return ''

def toResponseSuccess(data):
    response = {
        "code": 200,
        "body": {
            "code": "00000",
            "massageTH": "ทำรายการสำเร็จ",
            "massageEN": "Success",
            "data": data
        }
    }
    return response["body"],response["code"]
    