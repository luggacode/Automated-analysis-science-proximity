import json
from itertools import combinations
import os
from bokeh.plotting import figure
import geopandas as gpd

def file_exists(folder_path, filename):
    """
    Check if a file exists in the given folder.

    Parameters:
        folder_path (str): Path to the folder
        filename (str): Name of the file to check

    Returns:
        bool: True if the file exists, False otherwise
    """
    full_path = os.path.join(folder_path, filename)
    return os.path.isfile(full_path)

def get_topic_id(input_string):
    """
    Extracts the Topic ID (e.g.,) from a string like:
    'https://openalex.org/T10702'
    """
    # Split on '/' and take the last part
    topic_id = input_string.split("/")[-1]
    return topic_id

def get_length_works_file(path, filename):
    if file_exists(path, filename + '.json'):
        with open(str(path + filename) + ".json", "r", encoding="utf-8") as f:
            data = json.load(f)['results']
        count = int(len(data))
    else:
        count = 0
    return count


def all_sublists_descending(input_list):
    """
    Generate all possible sublists of input_list with lengths:
    n, n-1, n-2, ..., 1

    Parameters
    ----------
    input_list : list
        A list of n elements

    Returns
    -------
    dict
        Keys are sublist lengths, values are lists of sublists
    """
    n = len(input_list)
    result = {}

    for k in range(n, 0, -1):
        result[k] = [list(c) for c in combinations(input_list, k)]

    return result


def create_empty_map():
    map_url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    world = gpd.read_file(map_url)
    m = figure(title='Related Scientists Map', width=1200, # main_author[main_author_ID]['display_name']
            height=700, x_range=(-12000000, 9000000),
            y_range=(-1000000, 7000000),
            x_axis_type='mercator', y_axis_type='mercator',
            )
    m.add_tile("CartoDB Positron", retina=True)
    return m

