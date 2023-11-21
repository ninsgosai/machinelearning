# import os
# import cv2
# from paddleocr import PaddleOCR

# def extract_text_from_folder(folder_path):
#     # Initialize PaddleOCR
#     ocr = PaddleOCR()

#     for root, dirs, files in os.walk(folder_path):
#         for file in files:
#             image_path = os.path.join(root, file)

#             # Read the image using OpenCV
#             img = cv2.imread(image_path)

#             # Perform OCR
#             result = ocr.ocr(img)

#             # Extract text information from the result
#             extracted_text = ""
#             for line in result:
#                 for word_info in line:
#                     # Convert the tuple to a string
#                     word_text = word_info[-1][0]
#                     extracted_text += word_text + ' '

#             print(f'Text from {image_path}: {extracted_text}')

# if __name__ == "__main__":
#     folder_path = "/home/premal/Downloads/yolov5_latest/runs/detect/exp/crops"
#     extract_text_from_folder(folder_path)


from PIL import Image
import re
from flask import Flask,request
from flask import jsonify, make_response
import io
from PIL import ImageEnhance
from io import BytesIO
import cv2, os
from PIL import ImageEnhance, Image
import numpy as np
import os
import re
from datetime import datetime
from flask_cors import CORS
import json
import subprocess
import shutil
import time

app = Flask(__name__)
CORS(app)


@app.route("/paddle", methods = ['POST'])
def data_from_image():
    start_time = time.time()
    image_file = request.files['image']

    if image_file:
        allowed_extensions = {'.jpg', '.jpeg', '.png' , '.pdf' , '.webpg'}
        if image_file.filename.lower().endswith(tuple(allowed_extensions)):
            file_extension = os.path.splitext(image_file.filename)[-1]
            filename = os.path.splitext(image_file.filename)[0]

            project_dir = os.getcwd()

            folder_name = "license_images"

            folder_path = os.path.join(project_dir, folder_name)

            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

            file_name = f"{filename}{file_extension}"

            file_path = os.path.join(folder_path,file_name)

            image_file.save(file_path)

            command = ['python', 'detect.py', '--weights', '/home/premal/Downloads/yolov5_latest/runs/train/exp2/weights/best.pt', '--img', '416', '--conf','0.7','--source', file_path, '--save-txt', '--save-crop']

            result = subprocess.check_output(command)

            output_folder = 'runs/detect/exp' 

            output_dir_path = os.path.join(project_dir, output_folder)

            output_folder_name = 'output/output.json' 

            json_file_path = os.path.join(output_dir_path,output_folder_name)

            # Check if the JSON file exists
            if os.path.exists(json_file_path):
                # Open the JSON file and read data
                with open(json_file_path, 'r') as file:
                    json_data = json.load(file)
            else:
                json_data = {}

            print(json_data,'json_data')

            try:
                for key,value in json_data.items():
                    if key == 'DOB':
                        dob_data = value.split(' ')
                        date_pattern = r'\d{2}/\d{2}/\d{4}'
                        for element in dob_data:
                            match = re.search(date_pattern, element)
                            if match:
                                final_dob_data = element
                                
                    if key == "Address":
                        if not value.startswith('8'):
                            value = value.replace("8","",1)

                        try:
                            address = value.split('MA')
                            zip_code = address[1]
                            final_address = address[0].replace(",","")

                            if " " in zip_code:
                                zip_code = zip_code.replace(" ","")

                        except Exception as e:
                            return str(e)

                    if key == "License_number":
                        license_data = value.split(' ')
                        pattern = r'^(?=.*[A-Za-z])(?=.*\d).{3,}$'
                        for data in license_data:
                            if re.match(pattern, data) and len(data) > 5:
                                final_license_number = data

                    if key == "Name":
                        name_var = value.split(' ')
                        for data in name_var:
                            if data.strip():  # Check if data is not just whitespace
                                final_name = data
                                break

                    if key == "Surname":
                        cleaned_surname = re.sub(r'\d', '', value)

                        # Remove leading and trailing whitespaces
                        final_surname = cleaned_surname.strip()

                    
                final_dict = {
                    "Name": final_name,
                    "Surname": final_surname,
                    "Address": final_address,
                    "Zip_code" : zip_code,
                    "DOB" : final_dob_data,
                    "License_number" : final_license_number
                }
            except Exception as e:
                return str(e)


            response = make_response(jsonify(final_dict))
            response.status_code = 200

            # image_remove = os.remove(file_path)
            # crop_remove = shutil.rmtree(output_dir_path)

            end_time = time.time()  # Record the end time
            elapsed_time = end_time - start_time  # Calculate the elapsed time

            print(f"Time taken to generate response: {elapsed_time} seconds")

    
    return response



if __name__ == "__main__":
    app.run(debug=True,port=5009)









