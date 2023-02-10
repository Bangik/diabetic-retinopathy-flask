import os
from flask import Flask, request, redirect, url_for, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from src.classification_cnn import prediction
import sqlite3
import numpy as np

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
cors = CORS(app)
root_path = app.root_path
root_path = root_path.replace("\\", "/")

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('db/database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
	return redirect('http://localhost:5173')

@app.route('/last', methods=['GET'])
def last_data():
    try:
        conn = get_db_connection()
        posts = conn.execute('SELECT * FROM retina ORDER BY id DESC LIMIT 1').fetchall()
        conn.close()
        res = jsonify({"data":dict(ix) for ix in posts})
        res.status_code = 200
        return res
    except Exception as e:
        res = jsonify({'message' : 'Error while get data', 'error': str(e)})
        res.status_code = 400
        return res

@app.route('/history')
def history():
    try:
        conn = get_db_connection()
        posts = conn.execute('SELECT * FROM retina').fetchall()
        conn.close()
        res = jsonify({"data":[dict(ix) for ix in posts]})
        res.status_code = 200
        return res
    except Exception as e:
        res = jsonify({'message' : 'Error while get data', 'error': str(e)})
        res.status_code = 400
        return res

@app.route('/history/<int:id>', methods=['PUT'])
def update(id):
    try:
        if request.json['result'] == "":
            res = jsonify({'message' : 'Result is required'})
            res.status_code = 400
            return res
        
        conn = get_db_connection()
        conn.execute('UPDATE retina SET result = ? WHERE id = ?', (request.json['result'], id))
        conn.commit()
        conn.close()
        res = jsonify({'message' : 'Data updated successfully'})
        res.status_code = 200
        return res
    except Exception as e:
        res = jsonify({'message' : 'Error while update data', 'error': str(e)})
        res.status_code = 400
        return res

@app.route('/upload', methods=['POST'])
@cross_origin()
def upload_file():
	# check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message' : 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            prediction_result = prediction(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
            if prediction_result[0] == 0:
                result = "Normal"
            elif prediction_result[0] == 1:
                result = "NPDR Mild"
            elif prediction_result[0] == 2:
                result = "NPDR Moderate"
            elif prediction_result[0] == 3:
                result = "NPDR Severe"
            elif prediction_result[0] == 4:
                result = "PDR"
            else:
                result = "No Result"

            conn = get_db_connection()
            conn.execute('INSERT INTO retina (path, name, result, probability) VALUES (?, ?, ?, ?)',
                            (os.path.join(app.config['UPLOAD_FOLDER'], filename), filename, str(prediction_result[0]), str(prediction_result[1]))
                            )
            conn.commit()
            conn.close()

            resp = jsonify(
                {
                    'message' : 'File successfully uploaded',
                    'url_image': url_for('static', filename='uploads/' + filename, _external=True),
                    'prediction' : result,
                    'stage' : str(prediction_result[0]),
                    'probability' : str(prediction_result[1])
                }
            )
            resp.status_code = 201
            return resp
        except Exception as e:
            resp = jsonify({'message' : 'Error while uploading file', 'error': str(e)})
            resp.status_code = 400
    else:
        resp = jsonify({'message' : 'Allowed file types are png, jpg, jpeg, gif'})
        resp.status_code = 400
        return resp

if __name__ == "__main__":
    app.run()