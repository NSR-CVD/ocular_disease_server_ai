from Utilities.common import isEmpty, isInt, ExceptionError
from Utilities.errorCode import invalidErr


def mySchemaValidate(data):
    try:
        if isEmpty(data["data"]["tranId"]) == True:
            raise Exception(ExceptionError(invalidErr,'Tran Id Invalid Data',422))
        if (isEmpty(data["data"]["memberId"]) == True):
            raise Exception(ExceptionError(invalidErr,'Member Id Invalid Data',422))
        return True
    except Exception as error:
        raise Exception(error.args[0])