from flask import Flask
from upload_function import *
from werkzeug.utils import secure_filename

import random, os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image(file):
    filename = str(random.getrandbits(128)) + '.jpg'
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename)))
    return filename