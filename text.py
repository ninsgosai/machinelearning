import re
from flask import Flask,request
from flask import jsonify, make_response
import io
import cv2, os
import numpy as np
import os
import re
from flask_cors import CORS
import json
import subprocess
import time
import shutil

app = Flask(__name__)
CORS(app)


@app.route("/paddle", methods = ['POST'])
def data_from_image():
    start_time = time.time()
    image_file = request.files['image']

    if image_file:
        allowed_extensions = {'.jpg', '.jpeg', '.png' , '.pdf' , '.webpg'}
        if image_file.filename.lower().endswith(tuple(allowed_extensions)):
            try:
                file_extension = os.path.splitext(image_file.filename)[-1]
                filename = os.path.splitext(image_file.filename)[0]

                project_dir = os.getcwd()

                folder_name = "license_images"

                folder_path = os.path.join(project_dir, folder_name)

                if not os.path.exists(folder_path):
                    os.mkdir(folder_path)

                file_name = f"{filename}{file_extension}"

                file_path = os.path.join(folder_path,file_name)

                yolov5_model = "runs/train/exp2/weights/best.pt"

                model_path = os.path.join(project_dir,yolov5_model)

                image_file.save(file_path)

                command = ['python3', 'detect.py', '--weights', model_path, '--img', '416', '--conf','0.7','--source', file_path, '--save-txt', '--save-crop']

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
                
                # Initialize variables to None
                final_name = None
                final_surname = None
                final_address = None
                zip_code = None
                final_dob_data = None
                final_license_number = None
                final_sex = None

                try:
                    for key,value in json_data.items():
                        print("value.....", value)
                        if key == 'DOB':
                            dob_data = value.split(' ')
                            date_pattern = r'\b\d{2}[-/]\d{2}[-/]\d{4}\b'
                            for element in dob_data:
                                match = re.search(date_pattern, element)
                                if match:
                                    final_dob_data = element
                                
                        elif key == "Address":
                            value = value.strip()

                            # if value.startswith('8'):
                            #     value = value.replace("8","",1)

                            try:
                                zip_code_pattern = r'\b\d{5}(?:-\d{4})?\b'
                                matches = re.findall(zip_code_pattern, value)
                                if matches:
                                    for match in matches:
                                        zip_code = match
                                        text_zip = re.sub(zip_code_pattern, '', value)
                                        final_address = re.sub(r'\s+', ' ', text_zip).strip()
                                        
                                else:
                                    if any(char.isdigit() for char in value):
                                        value = re.sub(r'(?<=\D)(\d{5})', r' \1', value)

                                        zip_code_pattern = r'\b\d{5}(?:-\d{4})?\b'
                                        matches = re.findall(zip_code_pattern, value)
                                        if matches:
                                            for match in matches:
                                                zip_code = match
                                                text_zip = re.sub(zip_code_pattern, '', value)
                                                final_address = re.sub(r'\s+', ' ', text_zip).strip() 

                            except Exception as e:
                                return str(e)
                                
                        elif key == "License_number":
                            license_data = value.split(' ')
                            pattern = r'^(?=.*[A-Za-z])(?=.*\d).{3,}$'
                            number_pattern = r'^\d+$'
                            for data in license_data:
                                if re.match(pattern, data) and len(data) > 5:
                                    final_license_number = data
                                elif re.match(number_pattern, data) and len(data) > 5:
                                    final_license_number = data         

                        elif key == "Name":
                            name_var = value.split(' ')
                            for data in name_var:
                                if data.strip(): 
                                    final_name = data
                                    break

                        elif key == "Surname":
                            cleaned_surname = re.sub(r'\d', '', value)
                            final_surname = cleaned_surname.strip()

                        elif key == "Sex":
                            if 'M' in value or 'm' in value:
                                final_sex = 'M'
                            elif 'F' in value or 'f' in value:
                                final_sex = 'F'
                            
                        
                    final_dict = {
                        "Name": final_name,
                        "Surname": final_surname,
                        "Address": final_address,
                        "Zip_code" : zip_code,
                        "DOB" : final_dob_data,
                        "License_number" : final_license_number,
                        "SEX" : final_sex
                    }

                except Exception as e:
                    final_dict = {
                        "Name": final_name,
                        "Surname": final_surname,
                        "Address": final_address,
                        "Zip_code" : zip_code,
                        "DOB" : final_dob_data,
                        "License_number" : final_license_number,
                        "SEX" : final_sex
                    }
                    response = make_response(jsonify(final_dict))
                    response.status_code = 200
                    return response


                response = make_response(jsonify(final_dict))
                response.status_code = 200

                # image_remove = os.remove(file_path)
                # crop_remove = shutil.rmtree(output_dir_path)

                end_time = time.time()  # Record the end time
                elapsed_time = end_time - start_time  # Calculate the elapsed time

                print(f"Time taken to generate response: {elapsed_time} seconds")
        
                return response
            
            except Exception as e:
                final_dict = {
                   "output": f"{str(e)}"
                }
                response = make_response(jsonify(final_dict))
                response.status_code = 400
                return response
        
        else:
            final_dict = {
                "output": "Please provide valid image format"
            }
            response = make_response(jsonify(final_dict))
            response.status_code = 400
            return response
        
    else:
        final_dict = {
            "output": "Please provide valid image"
        }
        response = make_response(jsonify(final_dict))
        response.status_code = 404
        return response



if __name__ == "__main__":
    app.run(debug=True,port=5007)





# paddleocr>=2.7.0.3
# paddlepaddle>=2.5.2



