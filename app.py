from flask import Flask, request, render_template_string, send_from_directory
import cv2
import torch
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC_FOLDER'] = 'static'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def detect_vehicles_in_image(image_path):
    img = cv2.imread(image_path)
    results = model(img)
    vehicles = 0
    for obj in results.xyxy[0]:
        if obj[5] == 2:  # Class label 2 for cars in COCO dataset
            vehicles += 1
    output_image_path = os.path.join(app.config['STATIC_FOLDER'], os.path.basename(image_path))
    results.save(output_image_path)
    return vehicles, output_image_path

def calculate_processing_time(vehicles_count):
    # Each vehicle takes 3 seconds
    return vehicles_count * 3

index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vehicle Detection</title>
    <style>
        body {
            margin: auto;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            overflow: auto;
            background: linear-gradient(315deg, rgba(101,0,94,1) 3%, rgba(60,132,206,1) 38%, rgba(48,238,226,1) 68%, rgba(255,25,25,1) 98%);
            animation: gradient 15s ease infinite;
            background-size: 400% 400%;
            background-attachment: fixed;
        }

        @keyframes gradient {
            0% {
                background-position: 0% 0%;
            }
            50% {
                background-position: 100% 100%;
            }
            100% {
                background-position: 0% 0%;
            }
        }

        .wave {
            background: rgb(255 255 255 / 25%);
            border-radius: 1000% 1000% 0 0;
            position: fixed;
            width: 200%;
            height: 12em;
            animation: wave 10s -3s linear infinite;
            transform: translate3d(0, 0, 0);
            opacity: 0.8;
            bottom: 0;
            left: 0;
            z-index: -1;
        }

        .wave:nth-of-type(2) {
            bottom: -1.25em;
            animation: wave 18s linear reverse infinite;
            opacity: 0.8;
        }

        .wave:nth-of-type(3) {
            bottom: -2.5em;
            animation: wave 20s -1s reverse infinite;
            opacity: 0.9;
        }

        @keyframes wave {
            2% {
                transform: translateX(1);
            }

            25% {
                transform: translateX(-25%);
            }

            50% {
                transform: translateX(-50%);
            }

            75% {
                transform: translateX(-25%);
            }

            100% {
                transform: translateX(1);
            }
        }

        h1{
            text-align: center;
            font-size: 40px;
            background: white;
            padding: 20px 20px;
            margin: 40px 50px;
            border-radius: 10px;
        }
        form{
            display: flex;
            align-items: center;
            justify-content: center;
        }

        form input{
            font-size: 20px;
            border:none;
            outline: none;
        }
        form input.csfile{
        }
    </style>
</head>
<body>
    <h1>Upload an Image for Vehicle Detection</h1>
    <form action="/" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept="image/*">
        <input type="submit" value="Upload">
    </form>
</body>
</html>
"""
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            img_vehicles, output_image_path = detect_vehicles_in_image(filepath)
            processing_time = calculate_processing_time(img_vehicles)
            images = [{'filename': filename, 'vehicles': img_vehicles, 'processing_time': processing_time, 'path': output_image_path}]
            return render_template_string(result_html, images=images, image_path=output_image_path)
    return render_template_string(index_html)

result_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detection Result</title>
    <style>
        body {
            margin: auto;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            overflow: auto;
            background: linear-gradient(315deg, rgba(101,0,94,1) 3%, rgba(60,132,206,1) 38%, rgba(48,238,226,1) 68%, rgba(255,25,25,1) 98%);
            animation: gradient 15s ease infinite;
            background-size: 400% 400%;
            background-attachment: fixed;
            text-align: center; /* added to center the content */
        }

        @keyframes gradient {
            0% {
                background-position: 0% 0%;
            }
            50% {
                background-position: 100% 100%;
            }
            100% {
                background-position: 0% 0%;
            }
        }

        .wave {
            background: rgb(255 255 255 / 25%);
            border-radius: 1000% 1000% 0 0;
            position: fixed;
            width: 200%;
            height: 12em;
            animation: wave 10s -3s linear infinite;
            transform: translate3d(0, 0, 0);
            opacity: 0.8;
            bottom: 0;
            left: 0;
            z-index: -1;
        }

        .wave:nth-of-type(2) {
            bottom: -1.25em;
            animation: wave 18s linear reverse infinite;
            opacity: 0.8;
        }

        .wave:nth-of-type(3) {
            bottom: -2.5em;
            animation: wave 20s -1s reverse infinite;
            opacity: 0.9;
        }

        @keyframes wave {
            2% {
                transform: translateX(1);
            }

            25% {
                transform: translateX(-25%);
            }

            50% {
                transform: translateX(-50%);
            }

            75% {
                transform: translateX(-25%);
            }

            100% {
                transform: translateX(1);
            }
        }

        h1{
            text-align: center;
            font-size: 40px;
            background: white;
            padding: 20px 20px;
            margin: 40px 50px;
            border-radius: 10 px;
        }
        form{
            display: flex;
            align-items: center;
            justify-content: center;
        }

        form input{
            font-size: 20px;
            border:none;
            outline: none;
        }
        form input.csfile{
        }
        .image-container {
            margin: 20px;
        }
        .image-container img {
            width: 50%;
            height: 50%;
            border-radius: 10px;
        }
        .result-info {
            margin: 20px;
        }
    </style>
</head>
<body>
    <h1>Detection Result</h1>
    {% for image in images %}
    <div class="result-info">
        <p>Number of vehicles detected: {{ image.vehicles }}</p>
        <p>Detection time: {{ image.processing_time }} seconds</p>
    </div>
    {% endfor %}
    <form action="/" method="get">
        <input type="submit" value="Upload Another Image">
    </form>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)