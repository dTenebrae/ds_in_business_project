import os
import io
from os.path import join, dirname, realpath
import errno
import base64
from time import strftime
import logging
from logging.handlers import RotatingFileHandler

import torch
from PIL import Image, ImageOps
from torchvision import transforms

from flask import Flask, request, render_template, url_for, redirect
from werkzeug.utils import secure_filename

app = Flask(__name__)
IMG_FOLDER = join(dirname(realpath(__file__)), 'static/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = IMG_FOLDER

# logger initialization
handler = RotatingFileHandler(filename='app.log', maxBytes=100000, backupCount=10)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# load model and turn it in evaluation mode
MODEL_PATH = join(dirname(realpath(__file__)), 'models/digits_model.pth')
try:
    model = torch.load(MODEL_PATH)
    model.eval()
except FileNotFoundError as model_not_exist:
    dt_log = strftime("[%Y-%b-%d %H:%M:%S]")
    logger.warning(f'{dt_log} exception{model_not_exist} in path {MODEL_PATH}')
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                            MODEL_PATH) from model_not_exist


def get_prediction(image_var) -> tuple:
    r""" Returns predictions about loaded image (what digit it is) in form
    of a tuple of 2 elements. First element is a prediction itself,
    second - tensor of probabilities.
    Args:
        image_var: path to image to be recognized.
    Model expects 28 by 28 pixel image black digit on white background
    since it was trained on MNIST dataset. It will be resized and cropped tho.
    If not a str was passed as argument - it expected to be PIL Image object,
    since it's data recieved from canvas 
    TODO canvas feature not completed yet
    """

    # we have to describe Negative class to use it inside transforms.Compose
    # pipeline
    def to_negative(img_to_neg):
        img_to_neg = img_to_neg.convert('L')
        img_to_neg = ImageOps.invert(img_to_neg)
        img_to_neg = img_to_neg.convert('1')
        return img_to_neg

    class Negative(object):
        def __init__(self):
            pass

        def __call__(self, img_to_neg):
            return to_negative(img_to_neg)

    preprocess = transforms.Compose([
        transforms.Resize(32),  # Resize and crop incoming image to get
        transforms.CenterCrop(28),  # 28x28, which our model can eat
        transforms.Grayscale(),  # Turn in to greyscale
        Negative(),  # Since model was trained on MNIST dataset, image should be inverse grayscaled
        transforms.ToTensor(),  # No need to explain
        transforms.Normalize(0.5, 0.5)
    ])    

    # Check, if we got a path to image or image itself
    if isinstance(image_var, str):
        try:
            img = Image.open(image_var)
        except FileNotFoundError as image_not_exist:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                                    MODEL_PATH) from image_not_exist
    else:
        img = image_var

    # turn tensor in 2d array with [1, 784] shape
    img_processed = preprocess(img).flatten().unsqueeze(dim=0)

    with torch.no_grad():
        logps = model(img_processed)

    ps = torch.exp(logps)
    probab = list(ps.numpy()[0])
    return probab.index(max(probab)), probab


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#  check, if file extension is allowed
@app.route('/')
def main_page():
    return render_template('index.html')


@app.route('/load', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        dt = strftime("[%Y-%b-%d %H:%M:%S]")
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            logger.warning(f'{dt} empty path')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)  # TODO try/except this
            pred, prob = get_prediction(file_path)
            static_path = url_for('static', filename=f'uploads/{filename}')

            logger.info(f'{dt} Data: filepath={static_path}, prediction={pred}, probabilities={prob}')

            return render_template("load.html", uploaded_img=static_path, digit_pred=pred, prob_dist=prob)
    return render_template('load.html')


@app.route('/canvas', methods=['GET', 'POST'])
def canvas():
    return render_template('canvas.html')


#  function, what hook data from canvas, decode and send it to model.
#  atm sending just black(or white, not sure yet) rectangle, but incoming data looks proper
@app.route('/hook', methods=['POST'])
def get_image():
    image_b64 = request.values['imageBase64']
    image_data = image_b64.split(';')[1].split(',')[1]
    body = base64.decodebytes(image_data.encode('utf-8'))
    image_pil = Image.open(io.BytesIO(body))
    pred, prob = get_prediction(image_pil)
    print(pred)
    print(prob)
    return ''


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
