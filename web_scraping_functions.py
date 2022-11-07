import requests
import csv
from bs4 import BeautifulSoup
from file_functions import read_list, save_list

WARSPOTTING_VEHICLE_CODES = {
    'M113': [
        2,      # APC/IFV
        448,    # M113
    ],
    'MT-LB': [
        2,      # APC/IFV
        391,    # MT-LB*
        19,     # MT-LB
        538,    # MT-LB M1980 Blade
        21,     # MT-LB with ZU-23 AA gun
        22,     # MT-LBM 6MB
        24,     # MT-LBu
        20,     # MT-LBVM/K
    ],
    'BTR-80': [
        2,      # APC/IFV
        47,     # BTR-80
        511,    # BTR-80M
    ],
    'BTR-82A': [
        2,      # APC/IFV
        45,     # BTR-82A(M)
    ],
    'BMP-1': [
        2,      # APC/IFV
        356,    # BMP-1*
        37,     # BMP-1AM
        36,     # BMP-1P
        245,    # BMP-1TS
        246,    # BMP-1U 'Shkval'

    ],
    'BMP-2': [
        2,      # APC/IFV
        358,    # BMP-2*
        39,     # BMP-2 675-sb3KDZ
        38,     # BMP-2(K)
        450,    # BMP-2M
    ],
    'BMP-3': [
        2,      # APC/IFV
        41,     # BMP-3
    ],
    'T-62': [
        1,      # MBT
        366,    # T-62M
        489     # T-62MV
        ], 
    'T-64': [
        1,      # MBT
        351,    # T-64*
        228,    # T-64A
        229,    # T-64B
        230,    # T-64B1M
        231,    # T-64BM 'Bulat'
        232,    # T-64BM2 'Bulat'
        1,      # T-64BV
        414,    # T-64BV Zr. 2017
        508     # T-64BVK
        ],
    'T-72': [
        1,      # MBT
        352,    # T-72*
        233,    # T-72 Ural
        2,      # T-72A
        236,    # T-72AMT
        3,      # T-72AV
        4,      # T-72B
        5,      # T-72B Obr. 1989
        7,      # T-72B3
        468,    # T-72B3 Obr. 2014
        8,      # T-72B3 Obr. 2016
        6,      # T-72BA
        234     # T-72M/M1(R) 
        ],
    'T-80': [
        1,      # MBT
        353,    # T-80*
        9,      # T-80BV
        392,    # T-80BVK
        14,     # T-80BVM
        10,     # T-80U
        12,     # T-80UE-1
        11,     # T-80UK
        13,     # T-80UM2
        ],
    'T-90': [
        1,      # MBT
        354,    # T-90*
        15,     # T-90A
        16      # T-90M
        ],
    '2S1': [
        7,      # SPG
        121,    # 2S1 Gvozdika
        ],
    '2S3': [
        7,      # SPG
        122,    # 2S3(M) Akatsiya
        ],
    '2S19': [
        7,      # SPG
        123,    # 2S19 Msta-S
        124,    # 2S19M2 Msta-S
        ],
    'BM-21': [
        8,      # MLRS
        127,    # BM-21
        ],
}
WARSPOTTING_COUNTRY_CODES = {
    'Ukraine': 1,
    'Russia': 2,
    'Unknown': 3
}
WARSPOTTING_STATUS_CODES = {
    # 'unknown': 1,
    'abandoned': 2,
    'captured': 3,
    'destroyed': 4,
    'damaged': 5
}

def warspotting_scrape(vehicle_type):
    # Generates all of the URL combinations of said vehicle type.
    def url_generator():
        url_list = []
        base_url = 'https://ukr.warspotting.net/search/?'

        for code in WARSPOTTING_VEHICLE_CODES[vehicle_type]:
            vehicle_class = WARSPOTTING_VEHICLE_CODES[vehicle_type][0] # MBT, IFV, APC, SPG, MLRS
            if code != vehicle_class:
                for status_key, status_value in WARSPOTTING_STATUS_CODES.items():
                    for country_key, country_value in WARSPOTTING_COUNTRY_CODES.items():
                        url = base_url + 'weapon=' + str(vehicle_class) + '&model=' + str(code) + '&status=' + str(status_value) + '&belligerent=' + str(country_value) + '&page='
                        url_list.append(url)
        return url_list

    # Gets all of the images from one single page
    def image_scrape(url):
        r = requests.get(url, headers={'User-Agent': 'Chrome'})
        soup = BeautifulSoup(r.text,'html.parser')

        media_list = []

        images = soup.find_all('img')
        if images:
            for img in images:
                url = img['src']
                if '/media/thumbnails/' in url:
                    url = url.replace('/media/thumbnails/','https://ukr.warspotting.net/media/original/')
                media_list.append(url)
        return media_list    

    url_list = []
    url_list = url_generator()

    media_list = []
    new_media_list = []
    for url in url_list:
        page_number = 1
        url_with_page_number = url + str(page_number)
        media_list = image_scrape(url_with_page_number)

        if not media_list: # if empty
            continue
        while media_list != []:
            previous_media_list_length = len(media_list)
            page_number += 1
            url_with_page_number = url + str(page_number)
            media_list += image_scrape(url_with_page_number)
            if len(media_list) == previous_media_list_length:
                break

        if 'status=2' in url:
            status = 'abandoned'
        elif 'status=3' in url:
            status = 'captured'
        elif 'status=4' in url:
            status = 'destroyed'
        elif 'status=5' in url:
            status = 'damaged'
        else:
            status = 'unknown'
        
        for url in media_list:
            # [url, status, media_type, source]
            new_media_list.append([url, status, 'image', 'warspotting'])
    
    # Save data into URL jsons
    url_list = []
    url_list = read_list(vehicle_type)

    url_list += new_media_list

    save_list(vehicle_type, url_list)

    print(f'Added {len(new_media_list)} {vehicle_type} URLs to the list. Total number: {len(url_list)}')

ORYX_VEHICLE_NAMES = {
    'M113': ['M113'],
    '2S1': ['122mm 2S1 Gvozdika'],
    '2S3': ['152mm 2S3 Akatsiya','152mm 2S3(M) Akatsiya'],
    '2S19': ['152mm 2S19 Msta-S','152mm 2S33 Msta-SM2'],
}

# Function gets all of the links from the Oryx's .csv file that correspond to a vehicle of interest
def oryx_scrape(vehicle_type):

    def url_list_append(url, url_list):
        if 'i.postimg.cc/' in url: 
            url_list.append([url, status, 'image', 'oryx'])
        elif 'https://postimg.cc/' in url: 
            url_list.append([url, status, 'website', 'oryx'])
        elif 'pbs.twimg.com/media/' in url:
            url_list.append([url, status, 'image', 'twitter'])
        elif 'twitter.com/' in url:
            url_list.append([url, status, 'video', 'twitter'])
        else:
            url_list.append([url, status, 'unknown', 'unknown'])

    r = requests.get('https://raw.githubusercontent.com/scarnecchia/oryx_data/main/totals_by_system.csv')
    oryx_scrape_path = './dataset/oryx_scrape.csv'
    with open(oryx_scrape_path, 'wb') as f:
        f.write(r.content)

    counter = 0

    url_list = []
    url_list = read_list(vehicle_type)

    with open(oryx_scrape_path, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csv_reader:
            # Can't do list unpacking for some reason, so I have to do it this way
            system = row[2]
            status = row[3]
            url = row[4]

            if vehicle_type in ORYX_VEHICLE_NAMES: # This way we only get exact matches with Oryx's .csv, since some 9M113 ATGMs would end up in the M113 APC list, for example
                for key in ORYX_VEHICLE_NAMES:
                    for specific_name in ORYX_VEHICLE_NAMES[key]:
                        if specific_name in system:
                            counter += 1
                            # [url, status, media_type, source]
                            url_list_append(url, url_list)
            else:
                if vehicle_type in system:
                    counter += 1
                    # [url, status, media_type, source]
                    url_list_append(url, url_list)

    save_list(vehicle_type, url_list)
    print(f'Added {counter} {vehicle_type} URLs to the list. Total number: {len(url_list)}')

# warspotting_scrape('T-62')
# oryx_scrape('T-62')