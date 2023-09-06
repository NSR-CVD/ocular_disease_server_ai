from pathlib import Path
from datetime import date , timedelta
from keras.models import Sequential
from keras.layers import Dense, Flatten , Conv2D, MaxPool2D , Dropout , GaussianNoise
from sklearn.model_selection import train_test_split
from keras.metrics import Accuracy, Precision, Recall, AUC
import json
# from tensorflow.keras.preprocessing.image import ImageDataGenerator

import cv2
import numpy as np
import os
import tensorflow as tf
import configparser as cf
import time
import uuid
import sys
import pymysql
import boto3
from datetime import datetime

# MODEL_NOW = ''

print("Please select enviroment : dev,prd")
ENV = input("Select environment : ")
print("Please input model file name ")
MODEL_FILE = input("Model filename : ") 

if ENV == 'prd':
    setup = cf.ConfigParser()
    setup.read("config_prd.ini")
elif ENV == 'dev':
    setup = cf.ConfigParser()
    setup.read("config_dev.ini")
else: 
    print("Environment incorrect ...")
    sys.exit()

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
    
def get_dataset():
    cur , conn = connect_database()
    cur.execute("SELECT * FROM OCULAR_DATASET")
    rows = cur.fetchall()
    conn.close()
    return rows

def img2data():
    rows = get_dataset()
    rawImgs = []
    labels = []
    for idx , data in enumerate(rows):
        target_image_name = data[2].split("/") 
        img = cur_dir + '/training_data_temp/' + target_image_name[-1]
        exist = Path(img).is_file()
        # print(data)
        if exist == True:
            try:
                img_data = cv2.imread(img,cv2.COLOR_BGR2RGB)
                img_data = cv2.resize(img_data ,(255,255))
                if data[1] == 1:
                    rawImgs.append(img_data)
                    labels.append([1,0,0,0,0,0,0,0])
                elif data[1] == 2:
                    rawImgs.append(img_data)
                    labels.append([0,1,0,0,0,0,0,0])
                elif data[1] == 3:
                    rawImgs.append(img_data)
                    labels.append([0,0,1,0,0,0,0,0])
                elif data[1] == 4:
                    rawImgs.append(img_data)
                    labels.append([0,0,0,1,0,0,0,0])
                elif data[1] == 5:
                    rawImgs.append(img_data)
                    labels.append([0,0,0,0,1,0,0,0])
                elif data[1] == 6:
                    rawImgs.append(img_data)
                    labels.append([0,0,0,0,0,1,0,0])
                elif data[1] == 7:
                    rawImgs.append(img_data)
                    labels.append([0,0,0,0,0,0,1,0])
                elif data[1] == 8:
                    rawImgs.append(img_data)
                    labels.append([0,0,0,0,0,0,0,1])
                # print(img)
                print(idx+1," Read image success :",img , "Dianostic keywords : ",data[1])
            except Exception as error:
                print(error)
                continue
        else: 
            print(idx+1," Read image failed  :",img)
    return rawImgs,labels
    
def transform_data(test_data):
    a_train , b_train = img2data()
    x_train, x_test, y_train, y_test = train_test_split(a_train, b_train, test_size=test_data, random_state=42)
    x_train = np.array(x_train)
    y_train = np.array(y_train)
    x_test = np.array(x_test)
    y_test = np.array(y_test)

    print("###############################################################")
    print("Count number of train label : ", len(x_train))
    print("Count number of train feature : ", len(y_train))
    print("Shape of label : ",x_train.shape)
    print("Shape of feature : ",y_train.shape)
    print("Count number of test label : ", len(x_test))
    print("Count number of test feature : ", len(y_test))
    print("Shape of label : ",x_test.shape)
    print("Shape of feature : ",y_test.shape)
    print("###############################################################")
    return x_train, x_test, y_train, y_test

def predict(model_file,test_data, test_labels):
    cnn_from_pickle = tf.keras.models.load_model(cur_dir+"/model/"+model_file)
    test_loss, test_accuracy = cnn_from_pickle.evaluate(test_data, test_labels)
    print("Loss : " ,test_loss)
    print("Accu : " ,test_accuracy)

    # test_precision = Precision()(cnn_from_pickle, test_data, test_labels)
    # test_recall = Recall()(cnn_from_pickle, test_data, test_labels)
    # test_auc = AUC()(cnn_from_pickle, test_data, test_labels)

    # print('Test Precision: ', test_precision)
    # print('Test Recall: ', test_recall)
    # print('Test AUC: ', test_auc)

    return test_loss, test_accuracy

if __name__ == '__main__':
    try:
        checkpoint = 0
        # check file exist 

        os.system("mkdir "+ cur_dir + '/training_data_temp/')
        # print("Run command count file : ls -ld /content/drive/MyDrive/training_data_temp/* | wc -l")
        # count_data = os.system("ls -ld /content/drive/MyDrive/training_data_temp/* | wc -l")
        # print(count_data)
        print("Run command cp file : cp "+'/content/drive/MyDrive/training_data_temp/*' + ' '+ cur_dir + '/training_data_temp/')
        os.system("cp "+'/content/drive/MyDrive/training_data_temp/*' + ' '+ cur_dir + '/training_data_temp/')

        start = time.time()
        checkpoint = 1
        # download_all_images(BUCKET)
        end = time.time()
        print("")
        print("###############################################################")
        print("#   Elapsed time : {:42} #".format(end-start))
        print("###############################################################")
        print("")
        checkpoint = 2 
        x_train, x_test, y_train, y_test = transform_data(0.9)

        loss, accuracy = predict(MODEL_FILE,x_test,y_test)
        checkpoint = 3
        # accuracy = train_model(destination_path=model_path
        #                        ,feature_train=x_train
        #                        ,label_train=y_train
        #                        ,feature_test=x_test
        #                        ,label_test=y_test
        #                        )
        end = time.time()
        elapsed_time = end-start
        td = timedelta(seconds=elapsed_time)
        checkpoint = 4 
        id = int(uuid.uuid4().int & (1<<64)-2)
        # insert_into_model_master(id,model_path,accuracy[1] * 100 ,td,"Y",date.today(),None,None,None,None)
        print("")
        print("###############################################################")
        print("#   Elapsed time : {:42} #".format(end-start))
        print("###############################################################")
        print("")
    except Exception as error: 
        print("")
        print("###############################################################")
        print("#   Error step   : ",checkpoint)
        print(error)
        print("###############################################################")
        print("")
    # finally:
        # os.system("rm "+ cur_dir + '/training_data_temp/*.jpg')
