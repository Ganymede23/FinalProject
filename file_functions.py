import json
import os

#img_url.json has a list of lists. Each item has this structure: [url, status, media_type, source]

url_list = []

def save_list(vehicle_type, url_list):
    jsonString = json.dumps(url_list)
    # path = "./dataset/" + vehicle_type + "/img_urls.json"
    path = os.path.join('./dataset',vehicle_type,'img_urls.json')
    jsonFile = open(path, "w")
    jsonFile.write(jsonString)
    jsonFile.close()

def read_list(vehicle_type: str):
    # path = "./dataset/" + vehicle_type + "/img_urls.json"
    path = os.path.join('./dataset',vehicle_type,'img_urls.json')
    fileObject = open(path, "r")
    jsonContent = fileObject.read()
    try:
        url_list = json.loads(jsonContent)
    except:
        #json is empty
        url_list = []
        pass
    return url_list

def count_urls(vehicle_type):
    url_list = []
    url_list = read_list(vehicle_type)
    
    print(f'\tAmount of {vehicle_type} URLs: {len(url_list)}')