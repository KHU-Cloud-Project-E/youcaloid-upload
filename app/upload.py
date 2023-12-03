from flask import Flask, request, render_template, Response, jsonify
import os
import requests as req
from zipfile import ZipFile
import random
import string
from pasing import *
import shutil
from time import sleep


app = Flask(__name__)

UPLOAD_FOLDER = os.getenv('EFS_MOUNT_PATH', '/app/content')
ALLOWED_EXTENSIONS = {'zip'}
BACKEND_SERVER_URL = os.getenv('BACKEND_SERVER_URL', 'http://192.168.0.42:8080')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def generate_random_string(length=10):
    # 문자열이 구성될 문자 집합
    characters = string.ascii_letters + string.digits
    
    # 랜덤한 문자열 생성
    random_string = ''.join(random.choice(characters) for i in range(length))
    
    return random_string


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return 'root'


@app.route('/upload', methods=['POST'])
def upload_file():

    #response 설정
    content_type = "text/plain"

    #파일을 저장할 디렉토리
    uniq_dir : str = ""

    #authorization
    authkey = request.headers.get('Authorization')

    if 'model' not in request.files:
        return Response("No model file", status=400, content_type=content_type)
    
    if 'name' not in request.form:
        return Response("No model name", status=400, content_type=content_type)
    
    if authkey == None :
        return Response("Unauthorized", status=401, content_type=content_type)
    
    file = request.files['model']
    modelname = request.form['name']

    print("model name = " + modelname)
    
    if file.filename == '':
        return Response("No selected file", status=400, content_type=content_type)

    if file and allowed_file(file.filename):
        # Create a folder to store uploaded files if it doesn't exist
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        uniq_dir = app.config['UPLOAD_FOLDER'] + "/" +generate_random_string()
        while os.path.exists(uniq_dir):
            uniq_dir = app.config['UPLOAD_FOLDER'] + "/" +generate_random_string()
        os.makedirs(uniq_dir)

        # 경로 출력
        print("dir = " + uniq_dir + ", filename = " + file.filename)

        # Save the uploaded ZIP file
        zip_path = os.path.join(uniq_dir, file.filename)
        file.save(zip_path)

        # Extract the contents of the ZIP file
        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(uniq_dir)

        try :
            os.remove(zip_path)
        except Exception as e:
            print(zip_path + " : remov fail")
            shutil.rmtree(uniq_dir)

        # conf 파일 편집 및 pth 파일 추출시간
        pth_path = findBestPth(uniq_dir)
        print(pth_path)
        if pth_path == '':
            shutil.rmtree(uniq_dir)
            Response("do not have pth", status=400, content_type=content_type)
        
        if not updateConf(uniq_dir):
            shutil.rmtree(uniq_dir)
            return Response("invalid model zip", status=400, content_type=content_type)
        
        try :
            headers = {'Authorization': authkey}
            datas = {
                'path' : pth_path,
                'name' : modelname
            }
            backres = req.post(BACKEND_SERVER_URL + '/users/models', headers=headers, json=datas, verify=False)
            return backres.json

        except req.exceptions.RequestException as e:
            shutil.rmtree(uniq_dir)
            return jsonify({'error': str(e)})

        return Response("success", status=200, content_type=content_type)
    else:
        return Response("Invalid file type", status=400, content_type=content_type)


if __name__ == '__main__':
    app.run(debug=True)
