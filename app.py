import os
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
# import joblib
# from classification_svm import preprocessing, glcm
from classification_cnn import prediction

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
cors = CORS(app)
root_path = app.root_path
root_path = root_path.replace("\\", "/")

# model = joblib.load(os.path.join(root_path, 'static/model_ml/model_training.pkl'))

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_image():
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		return redirect(request.url)
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		#print('upload_image filename: ' + filename)
		flash('Image successfully uploaded and displayed below')
		return render_template('upload.html', filename=filename)
	else:
		flash('Allowed image types are -> png, jpg, jpeg, gif')
		return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/upload-image', methods=['POST'])
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
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # image = preprocessing(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename)
        # glcm_feature = glcm(image)


        prediction_result = prediction(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if prediction_result == 0:
            result = "Normal"
        elif prediction_result == 1:
            result = "NPDR Mild"
        elif prediction_result == 2:
            result = "NPDR Moderate"
        elif prediction_result == 3:
            result = "NPDR Severe"
        elif prediction_result == 4:
            result = "PDR"
        else:
            result = "No Result"

        resp = jsonify(
            {
                'message' : 'File successfully uploaded',
                'url_image': url_for('static', filename='uploads/' + filename, _external=True),
                # 'url_processed': url_for('static', filename='uploads/processed-' + filename, _external=True),
                'prediction' : result,
                'prediction_result' : int(prediction_result)
            }
        )
        resp.status_code = 201
        return resp
    else:
        resp = jsonify({'message' : 'Allowed file types are png, jpg, jpeg, gif'})
        resp.status_code = 400
        return resp

if __name__ == "__main__":
    app.run()