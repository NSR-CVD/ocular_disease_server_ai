import pymysql 
import csv
import boto3 
import joblib
import numpy as np
import tensorflow as tf
import cv2 
import configparser as cf 
import json 
import os
import datetime

# MODEL_NOW = ''

setup = cf.ConfigParser()
env = os.environ.get('FLASK_ENV', 'production')
if env == 'production':
    setup.read('config_prd.ini')
else:
    setup.read('config_dev.ini')

cur_dir = os.getcwd()
bucket = setup.get("AWS_S3","BUCKET")

def connect_database():
    try:
        conn = pymysql.connect(
        host=setup.get("DATABASE","HOSTNAME")
        ,user=setup.get("DATABASE","USER")
        ,password=setup.get("DATABASE","PASSWORD")
        ,db=setup.get("DATABASE","DB")
            )
        print('------------------------------------------')
        print("DATABASE CONNECTED")
        print('------------------------------------------')
        cur = conn.cursor() 
        return cur , conn 
    except Exception as error: 
        print('------------------------------------------')
        print("CANNOT CONNECT TO DATABASE ..")
        print('------------------------------------------')
        print(str(error))
        raise error

# def get_dataset():
#     cur , conn = connect_database()
#     cur.execute("SELECT * FROM RAW_OCULAR_DATASET")
#     rows = cur.fetchall()
#     conn.close()
#     return rows

#### DEVELOPING  #### 

def insert_into_summary(TRANSACTION_ID, MEMBER_ID, HOSPITAL_ID, ACTIVE_FLAG, PATIENT_ID, IMAGE_FULLNAME, OCULAR_TYPE, DIAGNOSIS_RESULT_1, DIAGNOSIS_RESULT_1_PERCENTAGE, DIAGNOSIS_RESULT_2, DIAGNOSIS_RESULT_2_PERCENTAGE, DIAGNOSIS_RESULT_3, DIAGNOSIS_RESULT_3_PERCENTAGE,DIAGNOSIS_MANUAL_UPDATE_FLAG, CREATE_DATE, CREATE_USER, UPDATE_DATE, UPDATE_USER): 
    cur , conn = connect_database()
    cur.execute(
        """
        INSERT INTO DIAG_TRANSACTION_SUMMARY (
            TRANSACTION_ID, MEMBER_ID, HOSPITAL_ID, ACTIVE_FLAG, PATIENT_ID, IMAGE_FULLNAME, OCULAR_TYPE, DIAGNOSIS_RESULT_1, DIAGNOSIS_RESULT_1_PERCENTAGE, DIAGNOSIS_RESULT_2, DIAGNOSIS_RESULT_2_PERCENTAGE, DIAGNOSIS_RESULT_3, DIAGNOSIS_RESULT_3_PERCENTAGE,DIAGNOSIS_MANUAL_UPDATE_FLAG, CREATE_DATE, CREATE_USER, UPDATE_DATE, UPDATE_USER) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
    (
        TRANSACTION_ID, MEMBER_ID, HOSPITAL_ID, ACTIVE_FLAG, PATIENT_ID, IMAGE_FULLNAME, OCULAR_TYPE, DIAGNOSIS_RESULT_1, DIAGNOSIS_RESULT_1_PERCENTAGE, DIAGNOSIS_RESULT_2, DIAGNOSIS_RESULT_2_PERCENTAGE, DIAGNOSIS_RESULT_3, DIAGNOSIS_RESULT_3_PERCENTAGE, DIAGNOSIS_MANUAL_UPDATE_FLAG, CREATE_DATE, CREATE_USER, UPDATE_DATE, UPDATE_USER
    ))
    print('------------------------------------------')
    print("INSERT INTO DIAG_TRANSACTION_SUMMARY ..")
    print('------------------------------------------')
    conn.commit()
    conn.close()

########################

def get_tranasction_info(transactionid):
    cur , conn = connect_database()
    print("get_tranasction_info :",transactionid)
    try: 
        cur.execute("SELECT TRANSACTION_ID , LEFT_IMAGE_NAME , RIGHT_IMAGE_NAME , MEMBER_ID , HOSPITAL_ID , PATIENT_ID FROM DIAG_TRANSACTION_REQUEST WHERE TRANSACTION_ID = '"+ transactionid +"'")
        rows = cur.fetchone()
        left_img = rows[1]
        right_img = rows[2]
        member_id = rows[3]
        hospital_id = rows[4]
        patient_id = rows[5]
    except Exception as error:
        print("Execute command failed")
        raise error
    conn.close()
    return left_img , right_img , member_id , hospital_id , patient_id 
    
def download_file_from_s3(bucket,filename,destination):
    print("S3 Information ",bucket, filename ,cur_dir + destination)
    try:
        KEY_ID = setup.get("AWS_KEY","KEY_ID")
        SECRET_KEY = setup.get("AWS_KEY","SECRET_KEY")
        s3 = boto3.client('s3',aws_access_key_id=KEY_ID,aws_secret_access_key=SECRET_KEY)
        # s3.download_file('health-me','model/model_cnn_2023-04-23.h5','/app/model/model_cnn_2023-04-23.h5')
        s3.download_file(bucket, filename ,cur_dir + destination)
    except Exception as error:
        print("DOWNLOAD FILE FROM S3",error)


# def remove_old_model():
#     global MODEL_NOW
#     print("REMOVEEEEEEEEEEEEEEEEEE",MODEL_NOW)
#     file_path = cur_dir+"/model/"+MODEL_NOW
#     print("remove_old_model",file_path)
#     try:
#         os.remove(file_path)
#         print(f"File '{file_path}' has been deleted.")
#     except FileNotFoundError:
#         print(f"File '{file_path}' not found.")
#     except PermissionError:
#         print(f"Permission denied to delete '{file_path}'.")
#     except Exception as e:
#         print(f"An error occurred while deleting '{file_path}': {e}")


def check_load_model_daily():

    # Check model file on local path 
    model_file_now = os.listdir(cur_dir + '/model/')
    # print(model_file_now)

    # Check active flag from database 
    cur , conn = connect_database()
    try:
        cur.execute("SELECT * FROM MODEL_MASTER WHERE ACTIVE_FLAG = 'Y'")
        rows = cur.fetchone()
        model_active_flag = rows[1].split('/')[-1]
    except Exception as Error:
        print(Error)
    conn.close()

    print("Model file now : ",model_file_now[0])
    print("Model file active flag : ",model_active_flag)

    # check name is equal or not 
    if model_file_now[0] != model_active_flag:
        print("Model now is not equal model active flag ")
        print("Download new model from S3 ")
        download_file_from_s3(bucket,'model/'+rows[1].split('/')[-1], '/model/'+rows[1].split('/')[-1])

        # remove old model 
        print("Remove old model ")
        os.remove(cur_dir + '/model/' + model_file_now[0])

        model_file_now[0] = model_active_flag
        print("Currently model name : ",model_file_now[0])
    else:
        print("Model is already up to date")

    return model_file_now[0]

# def check_load_model_daily():
#     cur , conn = connect_database()
#     try:
#         global MODEL_NOW
#         now = datetime.datetime.now()
#         if now.hour == 15 or MODEL_NOW == '':
#             print("It's 3 pm!")
#             cur.execute("SELECT * FROM MODEL_MASTER WHERE ACTIVE_FLAG = 'Y'")
#             rows = cur.fetchone()
#             print("check_load_model_daily",'/model/'+rows[1].split('/')[-1])
#             print("XXXXXXXXXXXXXXXXXXX",cur_dir+'/model/'+rows[1].split('/')[-1])
#             if MODEL_NOW != rows[1].split('/')[-1]:
#                 download_file_from_s3(bucket,'model/'+rows[1].split('/')[-1], '/model/'+rows[1].split('/')[-1])
#                 print(MODEL_NOW)
#                 if MODEL_NOW != '':
#                     remove_old_model()
#                 MODEL_NOW = rows[1].split('/')[-1]
#             return MODEL_NOW
#         else:
#             print("It's not 3 pm yet.")
#             return MODEL_NOW
#     except Exception as error:
#         print("Execute command failed") 
#         print("Exceptionnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn",error)
#         raise error
#     finally:
#         conn.close()

def validate_image(image):
    image = cv2.imread(image)
    HEIGHT , WIDTH , CHANNELS = image.shape
    if CHANNELS != 3 : 
        print("DIMENSION OF IMAGE CANNOT USE IN THIS PROGRAM.")
        exit()
    # return True

def img2predict(image):
    rawImgs = []
    try:
        image = cv2.imread(image , cv2.COLOR_BGR2RGB)
        image = cv2.resize(image ,(255,255))
    except: 
        print("Image not found")
    rawImgs.append(image)
    rawImgs = np.array(rawImgs)
    return rawImgs

def predict(input_data,model_file):
    # global MODEL_NOW
    cnn_from_pickle = tf.keras.models.load_model(cur_dir+"/model/"+model_file)
    cnn_from_pickle.compile(
              optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), 
              loss='categorical_crossentropy',
              metrics= ['accuracy'])
    diagnostic_keyword = [1, #'Diabetes',
        2, #'Pathological Myopia',
        3, #'Age related Macular Degeneration',
        4, #'Glaucoma',          # 
        5, #'Cataract',          
        6, #'Hypertension',      
        7, #'Normal',            
        8 #'Other diasease'     
    ]

    answer = cnn_from_pickle.predict(input_data) * 100
    print(answer)
    answer = sorted([(key, value) for i, (key, value) in enumerate(zip(answer[0], diagnostic_keyword))],reverse=True)
    answer = answer[0] + answer[1] + answer[2]
    print(answer)

    diagnostic_result_1 = json.dumps(str(answer[1])).strip('\\"')
    diagnostic_percentage_1 = json.dumps(str(answer[0])).strip('\\"')
    diagnostic_result_2 = json.dumps(str(answer[3])).strip('\\"')
    diagnostic_percentage_2 = json.dumps(str(answer[2])).strip('\\"')
    diagnostic_result_3 = json.dumps(str(answer[5])).strip('\\"')
    diagnostic_percentage_3 = json.dumps(str(answer[4])).strip('\\"')
    print("XXXX" ,diagnostic_result_1 , diagnostic_percentage_1 , diagnostic_result_2 , diagnostic_percentage_2 , diagnostic_result_3 , diagnostic_percentage_3)

    return diagnostic_result_1 , diagnostic_percentage_1 , diagnostic_result_2 , diagnostic_percentage_2 , diagnostic_result_3 , diagnostic_percentage_3
    # return input_data