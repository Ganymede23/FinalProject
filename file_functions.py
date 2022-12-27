import json
import grequests
import requests
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
    
    print(f'\t{vehicle_type}: {len(url_list)} URLs')


def make_image_requests(vehicle_type):
    url_list = read_list(vehicle_type)
    url_list = [item for item in url_list if item[2] == 'image'] # Keeps only images on the list
    url_only_list = [item[0] for item in url_list]

    req = (grequests.get(url, headers={'User-Agent': 'Chrome'}, timeout=60) for url in url_only_list)   # Generate the requests
    res = grequests.map(req)    # Get the responses on a list

    for index, url in enumerate(url_list):
        if res[index]:  # If there is a response (not None)
            url.append(res[index])  # Appends the response to the URL list item, so it's easier to download after with the rest of the data (source, status)
            url.append('grequests') # Appends request_type to each list item
        else:   # Sometimes grequests returns None (seems to happen after multiple requests in a short time). In that case we switch to sync requests
            r = requests.get(url[0], headers={'User-Agent': 'Chrome'})
            url.append(r)
            url.append('requests')

    # Output structure: list of lists -> [url, status, media_type, source, response, request_type]
    return url_list


def download_media(vehicle_type, verbose: bool = True):
    # Images
    counter_img_downloaded = 0
    counter_img_existed = 0

    failed_img_requests = []
    img_responses = make_image_requests(vehicle_type)
    for item in img_responses:
        # img_responses item structure: [url, status, media_type, source, response, request_type]
        url, status, media_type, source, response, request_type = item
        if response.status_code == 200:
            file_name_temp = url.split('/')
            if source == 'oryx':    # If source is Oryx then we concat the two parts of the URL, since the last one is not unique. 
                file_name = file_name_temp[-2] + file_name_temp[-1]
            else:                   # If source is either Twitter or Warspotting we can use just the last part. 
                file_name = file_name_temp[-1]
            full_path = os.path.join('./dataset/',vehicle_type,status,source,file_name) 
            if not os.path.exists(full_path):
                os.makedirs(os.path.dirname(full_path), exist_ok=True) # Creates folder if it doesn't exist previously
                with open(full_path, 'wb') as f:
                    f.write(response.content)
                counter_img_downloaded += 1
            else:
                # Picture already exists
                counter_img_existed += 1
        else:
            failed_img_requests.append(item)
    
    # Videos
        # Pending

    # Others
        # Pending

    if verbose:
        print(f'\t{vehicle_type}:')
        print(f'\t\tImages: {counter_img_downloaded} downloaded - {counter_img_existed} already existed - {len(failed_img_requests)} failed.')

    return [img_responses, failed_img_requests]