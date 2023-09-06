from flask import Flask, request, jsonify
# from controller import helloAndName  
from service.function import get_tranasction_info , insert_into_summary , download_file_from_s3 , check_load_model_daily
from service.function import validate_image , img2predict , predict , check_load_model_daily
from Utilities.common import ExceptionError
from datetime import datetime
from Utilities.errorCode import internalErr
import re
import configparser as cf 
import os 


# 'YYYY-MM-DD HH:mm:ss'

setup = cf.ConfigParser()
env = os.environ.get('FLASK_ENV', 'production')
if env == 'production':
    setup.read('config_prd.ini')
else:
    setup.read('config_dev.ini')

BUCKET = setup.get("AWS_S3","BUCKET")
DESTINATION = setup.get("AWS_S3","DESTINATION_DOWNLOADED_FILE")

print("Environment : ",env)
print("Bucket name : ",BUCKET)
print("Destination : ",DESTINATION)

def prediction(transactionid, memberId):
    try: 
        # Get information from database 
        check_load_model_daily()
        checkpoint = 1
        left_imgname , right_imgname , memberid , hospitalid , patientid = get_tranasction_info(transactionid)
        left_destination = re.split('/',left_imgname)
        right_destination = re.split('/',right_imgname)

        # Download Image from S3
        checkpoint = 2
        download_file_from_s3(BUCKET, left_destination[-2]+'/'+left_destination[-1] , DESTINATION+left_destination[-1]) 
        download_file_from_s3(BUCKET, right_destination[-2]+'/'+right_destination[-1] , DESTINATION+right_destination[-1]) 

        # Validate image   
        checkpoint = 3
        validate_image(os.getcwd()+DESTINATION+left_destination[-1])
        validate_image(os.getcwd()+DESTINATION+right_destination[-1])

        # Read image after downloaded
        checkpoint = 4 
        data_left_image = img2predict(os.getcwd()+DESTINATION+left_destination[-1])
        data_right_image = img2predict(os.getcwd()+DESTINATION+right_destination[-1])

        # Predict Image 
        model_name = check_load_model_daily()
        checkpoint = 5 
        left_diag_1, left_percent1, left_diag_2, left_percent2, left_diag_3, left_percent3  = predict(data_left_image,model_name)
        right_diag_1, right_percent1, right_diag_2, right_percent2, right_diag_3, right_percent3 = predict(data_right_image,model_name)

        print("Left diagnosis : ",left_diag_1, left_percent1, left_diag_2, left_percent2, left_diag_3, left_percent3 )
        print("Right diagnosis : ",right_diag_1, right_percent1, right_diag_2, right_percent2, right_diag_3, right_percent3)
        # Insert into summary 
        checkpoint = 6
        insert_into_summary(TRANSACTION_ID=transactionid, 
            MEMBER_ID=memberid, 
            HOSPITAL_ID=hospitalid, 
            ACTIVE_FLAG='Y', 
            PATIENT_ID=patientid, 
            IMAGE_FULLNAME=left_imgname, 
            OCULAR_TYPE='LEFT', 
            DIAGNOSIS_RESULT_1=left_diag_1, 
            DIAGNOSIS_RESULT_1_PERCENTAGE=left_percent1, 
            DIAGNOSIS_RESULT_2=left_diag_2, 
            DIAGNOSIS_RESULT_2_PERCENTAGE=left_percent2, 
            DIAGNOSIS_RESULT_3=left_diag_3, 
            DIAGNOSIS_RESULT_3_PERCENTAGE=left_percent3,
            DIAGNOSIS_MANUAL_UPDATE_FLAG='N', 
            CREATE_DATE=datetime.now(), 
            CREATE_USER=memberid, 
            UPDATE_DATE=datetime.now(), 
            UPDATE_USER=memberid
        )

        checkpoint = 7
        insert_into_summary(TRANSACTION_ID=transactionid, 
            MEMBER_ID=memberid, 
            HOSPITAL_ID=hospitalid, 
            ACTIVE_FLAG='Y', 
            PATIENT_ID=patientid, 
            IMAGE_FULLNAME=right_imgname, 
            OCULAR_TYPE='RIGHT', 
            DIAGNOSIS_RESULT_1=right_diag_1, 
            DIAGNOSIS_RESULT_1_PERCENTAGE=right_percent1, 
            DIAGNOSIS_RESULT_2=right_diag_2, 
            DIAGNOSIS_RESULT_2_PERCENTAGE=right_percent2, 
            DIAGNOSIS_RESULT_3=right_diag_3, 
            DIAGNOSIS_RESULT_3_PERCENTAGE=right_percent3,
            DIAGNOSIS_MANUAL_UPDATE_FLAG='N', 
            CREATE_DATE=datetime.now(), 
            CREATE_USER=memberid, 
            UPDATE_DATE=datetime.now(), 
            UPDATE_USER=memberid
        )
        return transactionid

    except Exception as error: 
        print(jsonify({"error": str(error)}))
        print("Step", checkpoint , "Process failed")
        raise ExceptionError(internalErr,str(error),500)
    finally:
        # Remove temp file  
        os.remove(os.getcwd()+DESTINATION+left_destination[-1])
        os.remove(os.getcwd()+DESTINATION+right_destination[-1])
