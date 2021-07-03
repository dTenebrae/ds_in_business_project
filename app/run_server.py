import os
from os.path import join, dirname, realpath
import errno
from time import strftime
import logging
from logging.handlers import RotatingFileHandler

import torch
from PIL import Image
from torchvision import transforms

from flask import Flask, request, render_template, flash, url_for, redirect, send_from_directory
from werkzeug.utils import secure_filename


# global declaration
IMG_FOLDER = join(dirname(realpath(__file__)), 'uploads/')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = IMG_FOLDER
# app.add_url_rule(
#     "/uploads/<name>", endpoint="download_file", build_only=True
# )

# load model and turn it in evaluation mode
MODEL_PATH = './app/models/digits_model.pth'  # TODO: make path dynamic
try:
    model = torch.load(MODEL_PATH)
    model.eval()
except FileNotFoundError as model_not_exist:
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                            MODEL_PATH) from model_not_exist



def get_prediction(image_path: str) -> tuple:
    r""" Returns predictions about loaded image (what digit it is) in form
    of a tuple of 2 elements. First element is a prediction itself,
    second - tensor of probabilities.
    Args:
        image_path: path to image, which should be recognized.
    Model expects 28 by 28 pixel image, since it was trained on MNIST
    dataset. It will be resized and cropped tho.
    """

    preprocess = transforms.Compose([
        transforms.Resize(29),      # Resize and crop incoming image to get
        transforms.CenterCrop(28),  # 28x28, which our model can eat
        transforms.Grayscale(),     # Turn in to greyscale
        transforms.ToTensor()       # No need to explain
    ])

    try:
        img = Image.open(image_path)
    except FileNotFoundError as image_not_exist:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                                MODEL_PATH) from image_not_exist

    # turn tensor in 2d array with [1, 784] shape
    img_processed = preprocess(img).flatten().unsqueeze(dim=0)

    predictions = model(img_processed)
    return predictions.argmax().item(), predictions


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def main_page():
    return render_template('index.html')

# @app.route('/uploads/<name>')
# def download_file(name):
#     return send_from_directory(app.config["UPLOAD_FOLDER"], name)

# @app.route('/')
@app.route('/load', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            print(file_path)
            return render_template("load.html", uploaded_img = file_path)
    return render_template('load.html')


@app.route('/canvas', methods=['GET', 'POST'])
def canvas():
    return render_template('canvas.html')

# @app.route('/')
# def predict():
#     pred, _ = get_prediction('./app/img/digit.png')
#     return f'{pred}'


if __name__ == '__main__':
    app.run(debug=True)

