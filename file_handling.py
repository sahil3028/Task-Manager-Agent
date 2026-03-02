import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "data.json")

def load_file(user):
    with open(FILE_PATH,'r') as file:
        data=json.load(file)

    return data.get(user,[])

def save_file(user, tasks):

        data={}
        with open(FILE_PATH,'r') as file:
            data=json.load(file)

            data[user]=tasks

        with open(FILE_PATH,'w') as file:
            json.dump(data,file,indent=4)