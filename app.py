from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename
from LSBSteg import *

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/options')
def options():
    return render_template('options.html')


@app.route('/encode')
def encode():
    return render_template('encode.html')


@app.route('/decode')
def decode():
    return render_template('decode.html')


@app.route('/result')
def result():
    return render_template('result.html')


@app.route('/encode_image', methods=['POST'])
def encode_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    message = request.form['message']
    file = request.files['file']
    if message == '':
        flash('No message found')
        return redirect(request.url)
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # encoding
        stag = LSBSteg(cv2.imread('static/uploads/' + filename))
        img_encoded = stag.encode_text(message)
        cv2.imwrite("my_new_image.png", img_encoded)

        # print('upload_image filename: ' + filename)
        # flash('Image successfully uploaded and displayed below')
        return render_template('result.html', filename=filename, op='encoding', msg=message)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/decode_image', methods=['POST'])
def decode_image():
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

        # decoding
        im = cv2.imread('static/uploads/' + filename)
        stag = LSBSteg(im)
        rst = stag.decode_text()
        if rst == '':
            value = 'No Information Found in the Image'
        else:
            value = rst

        # print('upload_image filename: ' + filename)
        # flash('Image successfully uploaded and displayed below')
        return render_template('result.html', filename=filename, op='decoding', msg=value)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    # print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == "__main__":
    app.run(debug=True)
