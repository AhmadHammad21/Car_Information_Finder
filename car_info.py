"""
modules and packages
pip install requests
pip install beautifulsoup4
pip install opencv-contrib-python
pip install numpy as np
"""
import requests
from pprint import pprint
from bs4 import BeautifulSoup
import json
import cv2 
import numpy as np


def get_plate_number_and_coordinates(image):

	regions = ['in', 'us-ca'] # Change to your country
	with open(image, 'rb') as fp:
	    response = requests.post(
	        'https://api.platerecognizer.com/v1/plate-reader/',
	        data=dict(regions=regions),  # Optional
	        files=dict(upload=fp),
	        headers={'Authorization': 'Token d87f36fd283273953ea58fa630143c1bef7f2dd0'})

	#pprint(response.json()) # this shows the whole response

	plate_number = response.json()['results'][0]['plate'] # Extracting number of the plate
	vehicle_coordinates = response.json()['results'][0]['vehicle']['box']

	vals = list(vehicle_coordinates.values())
	start_veh, end_veh = (vals[0], vals[1]), (vals[2], vals[3])

	number_coordinates = response.json()['results'][0]['box']
	vals = list(number_coordinates.values())
	start_num, end_num = (vals[0], vals[1]), (vals[2], vals[3])


	return plate_number, start_num, end_num, start_veh, end_veh


def car_registration_info(plate_number, username):

	with open('car.png', 'rb') as fp:
	    response = requests.get(
	        'http://www.carregistrationapi.in/api/reg.asmx/CheckIndia?RegistrationNumber={}&username={}'.format(plate_number, username),
	       )

	xml = response.content
	f =  open("data.xml", "wb")
	f.write(xml)
	f.close()

	return "data.xml"


def extracted_car_data(xml, plate_number):
	with open(xml, 'r') as f:
		data = f.read()
 
	# Passing the stored data inside
	# the beautifulsoup parser, storing
	# the returned object
	Bs_data = BeautifulSoup(data, "xml")


	b_unique = Bs_data.find_all('vehicleJson')

	h = b_unique[0].text
	d = json.loads(h)


	LABELS = ['PlateNumber', 'RegistrationYear', 'Location', 'RegistrationDate', 'CarModel', 'PUCC', 'Owner', 'Insurance', 'VehicleType', 'FuelType', 'EngineSize', 'MakeDescription']
	final_d = {}

	d['FuelType'] =  d['FuelType']['CurrentTextValue']
	d['CarModel'] = d['CarModel']['CurrentTextValue']
	d['EngineSize'] = d['EngineSize']['CurrentTextValue'] + "CC"
	d['MakeDescription'] = d['MakeDescription']['CurrentTextValue']
	d['PlateNumber'] = plate_number

	for label in LABELS:
		if len(d[label]) == 0: #if empty
			d[label] = "-"
		final_d[label] = d[label]


	return final_d


def draw_boxes(image, start_num, end_num, start_veh, end_veh):
	GREEN = (0, 128, 0)
	YELLOW = (0, 255, 255)
	# Reading an image in default mode
	image = cv2.imread(image)
	   
	# Window name in which image is displayed
	window_name = 'Result_Car'
	  
	# Line thickness of 2 px
	thickness = 2
	
	# Using cv2.rectangle() method
	# Draw a rectangle with blue line borders of thickness of 2 px
	image = cv2.rectangle(image, start_num, end_num, YELLOW, thickness)
	image = cv2.rectangle(image, start_veh, end_veh, GREEN, thickness)
	new_image_name = "result_car.png"

	# Displaying the image 
	#cv2.imshow(window_name, image)
	# Saving the image
	cv2.imwrite(new_image_name, image)
	
	
	blank_image = cv2.imread(new_image_name)
	new_height = image.shape[0] + 200
	new_width = image.shape[1]
	new_image = check_image(blank_image, new_height, new_width)
	cv2.imwrite(new_image_name, new_image)
	return new_image_name, new_height, new_width
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()


def check_image(image: np.array, new_height: int, new_width: int):
    height = image.shape[0]
    width = image.shape[1]
    colour = image.shape[2]
    BLACK_COLOUR = [0] * colour
    if height == new_height and width == new_width:
        return image
    imageList = image.tolist()
    one_column = [BLACK_COLOUR] * new_width
    for row in imageList:
        if len(row) < new_width:
            row.extend([BLACK_COLOUR] * (new_width - len(row)))
    imageList.extend([one_column] * (new_height - len(imageList)))
    return np.array(imageList)


def put_text(img, text_height, text_width, dict_data):
	image = cv2.imread(img)
	text_height = 0
	coordinates = (text_height, text_width - 375)
	font = cv2.FONT_HERSHEY_SIMPLEX
	fontScale = 0.8
	color = (0, 69, 255)
	thickness = 2
	line_type = cv2.LINE_AA
	text = "Information"

	text_size, _ = cv2.getTextSize(text, font, fontScale, thickness)
	line_height = text_size[1] + 5
	x, y0 = coordinates
	count = 0
	for i, line in enumerate(extracted_data.items()):
		line = f"{line[0]} : {line[1]}"
		y = y0 + i * line_height
		if i >= 8:
			y = y0 + line_height * count
			x = int(text_width / 2) + 50
			count += 1
		#print(x, y)
		cv2.putText(image,
	                line,
	                (x, y),
	                font,
	                fontScale,
	                color,
	                thickness,
	                line_type)

	cv2.imwrite(img, image)
	cv2.imshow("car_result", image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()


car_img = "car.png"

# if the code shows error, this is somehow due to no credit in carregistrationapi, so make an account
# and put the username down below, and it's going to work for sure
username = "ahmadhammadtest123" # 5 credits left to use the api, so it's valid for more 5 runs only using "https://www.carregistrationapi.in/"


plate_number, start_num, end_num, start_veh, end_veh = get_plate_number_and_coordinates(car_img)

xml = car_registration_info(plate_number, username)

extracted_data = extracted_car_data(xml, plate_number)

new_car_img, text_height, text_width = draw_boxes(car_img, start_num, end_num, start_veh, end_veh)

put_text(new_car_img, text_height, text_width, extracted_data)


	

