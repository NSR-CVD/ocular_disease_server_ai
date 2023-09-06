from flask import Flask, request
from Validate.MySchema import mySchemaValidate
from Utilities.common import exToResponse, toResponseSuccess
from Controller.controller import prediction
import os
import configparser as cf 

app = Flask(__name__) 

setup = cf.ConfigParser()
env = os.environ.get('FLASK_ENV', 'production')
if env == 'production':
    setup.read('config_prd.ini')
else:
    setup.read('config_dev.ini')

@app.route('/', methods=['GET']) 
def index():
    return { "message": "Hello!" }, 200

@app.route('/ai/api/checkenv', methods=['GET'])
def checkroute():
    return { "message": setup.get("ENV","ENV_HOST") }, 200

@app.route('/ai/api/upload/proces', methods=['POST'])
def controller():
    data = request.json
    prefix = "tranid : " + data["data"]["tranId"] + ' | member id : ' + str(data["data"]["memberId"]) + ' | function : controller | '
    print(prefix,"request data : " ,data)
    mySchemaValidate(data)

    try:
        result = prediction(data["data"]["tranId"], str(data["data"]["memberId"]))
        if result == None:
            raise Exception
        response = {
                "data": {
                    "tranId": result
                }
            }
        return toResponseSuccess(response["data"]["tranId"])
    except Exception as error:
        print(error)
        return exToResponse(str(error))

@app.route('/ai/api/health-check', methods=['GET'])
def healthCheck():
    return { "message": "Checked!" }, 200

if __name__ == '__main__':
    print("Server is running ... ")
    print("Environment : ",env)
    app.run(debug = True, host='0.0.0.0', port=3000)