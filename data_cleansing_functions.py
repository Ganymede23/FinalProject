# Data cleansing functions

from itertools import combinations
from file_functions import read_list, save_list

# Function deletes all duplicate URLs by turning List into a Set.

def remove_url_duplicates(vehicle_type):
    # First chunk deletes exact duplicates
    url_list = []
    url_list = read_list(vehicle_type)

    initial_amount = len(url_list)
    url_list = [list(item) for item in set(tuple(row) for row in url_list)] # Turns the list of lists into a set to rule out duplicates
    # url_list = list(set(url_list))
    final_amount = len(url_list)

    # Second chunk deletes cases where the URL is the same and keeps the item with status information
    # This happens usually when we have a URL retrieved from the Twitter API with status 'unknown', and the same one from Oryx's site
    url_only_list = [item[0] for item in url_list]
    discarded_urls = []

    if len(url_only_list) != len(set(url_only_list)):
        for item in combinations(url_list, 2):
            item1, item2 = item
            url1, status1, _, _ = item1
            url2, status2, _, _ = item2
            if url1 == url2:
                if status1 == 'unknown':
                    discarded_urls.append(item1)
                else:
                    discarded_urls.append(item2)
        
    url_list = [item for item in url_list if item not in discarded_urls]

    save_list(vehicle_type, url_list)
    print(vehicle_type, '-', (initial_amount-final_amount)+len(discarded_urls), 'duplicated URLs deleted.')

#remove_url_duplicates('M113')

# Function removes all non-twitter URLs from .json files and applies the new structure to the data. Done to include status, media type and source to each URL.
# [url, status, media_type, source]
def clear_url_list(vehicle_type):
    url_list = []
    url_list = read_list(vehicle_type)
    new_url_list = []

    for item in url_list:
        # [url, status, media_type, source]
        if isinstance(item, list):
            new_url_list.append(item)
        else:
            if item is not None:
                if 'pbs.twimg.com/media/' in item:  # if the media URL belongs to an image
                    new_item = [item, 'unknown', 'image', 'twitter']
                    new_url_list.append(new_item)
                elif 'twitter.com/' in item:        # if the media URL belongs to a video
                    new_item = [item, 'unknown', 'video', 'twitter']
                    new_url_list.append(new_item)
    save_list(vehicle_type, new_url_list)

# Function removes all non-twitter URLs from .json files. Leaves data structure as is.
def remove_all_but_twitter_urls(vehicle_type):
    url_list = []
    url_list = read_list(vehicle_type)
    new_url_list = []
    for item in url_list:
        url, status, media_type, source = item
        if source != 'oryx' and source != 'unknown':
            new_url_list.append(item)
    save_list(vehicle_type, new_url_list)