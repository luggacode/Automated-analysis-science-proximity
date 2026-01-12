import requests
import os
import json
from bokeh.io import output_notebook, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from pyproj import Proj, transform
import geopandas as gpd
from shapely.geometry import Point
from useful_methods import file_exists

def extract_openalex_id(input_string):
    """
    Extracts the OpenAlex ID (e.g., A5063212181) from a string like:
    'Authors/https://openalex.org/A5063212181.json'
    """
    # Split on '/' and take the last part
    last_part = input_string.split("/")[-1]
    # Remove the '.json' suffix
    openalex_id = last_part.replace(".json", "")
    return openalex_id

def get_content_from_request(url, filename):
    """
    saves data from API request to json-file
    """
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        with open(str(filename) + ".json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    else:
        print("Request failed:", response.status_code)

def get_works_from_request(url, content) ->  dict:
    """
    saves data from API request to json-file
    """
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        content['results'].extend(data['results'])
    else:
        print("Request failed:", response.status_code)
    
    return content
    

def get_institution(file):
    """
    Returns ror-ID of the last known institution of a researcher in his records
    """
    content = None
    with open(str(file) + ".json", "r", encoding="utf-8") as f:
        data = json.load(f)
        try: 
            content = data['last_known_institutions'][0]['ror']
        except (KeyError, IndexError, TypeError):
            try:
                vergleichsjahr = 0
                for ind, aff in enumerate(data['affiliations']):
                    year = int(data['affiliations'][ind]['years'][0])
                    if vergleichsjahr < year:
                        content = data['affiliations'][ind]['institution']['ror']
                        vergleichsjahr = year
            except (KeyError, IndexError, TypeError):
                content = None
    return content

def get_coordinates(file):
    """
    Returns longitude and latitude of an institutions ror-file 
    """
    with open(str(file) + ".json", "r", encoding="utf-8") as f:
        content = json.load(f)['locations'][0]['geonames_details']
        latitude = content['lat']
        longitude = content['lng']
    return latitude, longitude

def get_author_info(file):
    """
    Returns dict with relevant information in the researchers records
    """
    information = {
        "display_name": "",
        "works_count": "",
        "cited_by_count": ""
    }
    with open(str(file) + ".json", "r", encoding="utf-8") as f:
        content = json.load(f)
        for key in information:
            information[key] = content[key]
    return information

def get_related_authors(author_ID):
    """
    Returns a dict of every author who has published with a main author plus the main author him/herself
    """
    get_content_from_request('https://api.openalex.org/works?filter=author.id:' + str(author_ID), 'Works_' + str(author_ID))
    related_authors = {}
    with open('Works_' + str(author_ID) + '.json') as f:
        content = json.load(f)['results']
        for work in content:
            for authorship in work['authorships']:
                if not authorship['author']['id'] in related_authors:
                    if not authorship['author']['id'] == None:
                        ID = extract_openalex_id(authorship['author']['id'])
                        related_authors[ID] = authorship['author']
    return related_authors

def get_institution_location(author_ID):
    """
    Returns longitude and latitude of an authors institution based on their OpenAlexID
    """
    print(author_ID)
    institution_ID = get_institution('Authors/' + str(author_ID))
    if not institution_ID == None:
        get_content_from_request('https://api.ror.org/v2/organizations/' + institution_ID, 'Institutions/institution_' + str(author_ID))
        lat, lng = get_coordinates('Institutions/institution_' + str(author_ID))
    else:
        lat = 0
        lng = 0
    return lat, lng

def point_in_country(lat, lon, country_name, world):
    """
    Checks if point is in a country
    """
    country = world[world["NAME"] == country_name]
    point = Point(lon, lat)
    return country.contains(point).any()

# map_url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
# world = gpd.read_file(map_url)





# # AUTHOR INPUT AND API URL 
# main_author_name = "Jan-Henning Dirks"
# author_url = "https://api.openalex.org/authors/A5063212181"
# main_author_ID = 'A5063212181'


# # GET API INFO AND SAFE TO JSON
# # current author name sündüs
# info_list = get_related_authors(main_author_ID)

# for author in info_list:
#     if not file_exists('Authors/', author + '.json'):
#         get_content_from_request("https://api.openalex.org/authors/" + str(author), 'Authors/' + str(author))
#     info_list[author] = get_author_info('Authors/' + str(author))
#     lat, lng = get_institution_location(author)
#     info_list[author]['lat'] = lat
#     info_list[author]['lng'] = lng


# # Initializing pyproj for Converting from longitude,
# # latitude to native map projection x, y coordinates.
# outProj = Proj(init='epsg:4326')
# inProj = Proj(init='epsg:3857')

# # Converting Longitude and Latitude to x,y coordinates.
# for author in info_list:
#     lng = float(info_list[author]['lng'])
#     lat = float(info_list[author]['lat'])
#     info_list[author]['coords_lng'], info_list[author]['coords_lat'] = transform(outProj, inProj, lng, lat)

# related_authors = {
#     k: v for k, v in info_list.items()
#     if k != main_author_ID
# }
# print(related_authors)

# main_author = {
#     k: v for k, v in info_list.items()
#     if k == main_author_ID
# }

# node_source_related_authors = ColumnDataSource(data=dict(    
#     x=[related_authors[author]['coords_lng'] for author in related_authors],
#     y=[related_authors[author]['coords_lat'] for author in related_authors],
#     scientist = [related_authors[author]['display_name'] for author in related_authors],
#     works = [related_authors[author]['works_count'] for author in related_authors],
#     citations = [related_authors[author]['cited_by_count'] for author in related_authors]
# ))

# node_source_main_authors = ColumnDataSource(data=dict(    
#     x=[main_author[author]['coords_lng'] for author in main_author],
#     y=[main_author[author]['coords_lat'] for author in main_author],
#     scientist = [main_author[author]['display_name'] for author in main_author],
#     works = [main_author[author]['works_count'] for author in main_author],
#     citations = [main_author[author]['cited_by_count'] for author in main_author]
# ))

# # Creating Map object.
# m = figure(title='Related Scientists Map ' + main_author[main_author_ID]['display_name'], width=1400, 
#            height=700, x_range=(-12000000, 9000000),
#            y_range=(-1000000, 7000000),
#            x_axis_type='mercator', y_axis_type='mercator',
#            )
# m.add_tile("CartoDB Positron", retina=True)

# node_renderer_1 = m.scatter(
#     x="x",
#     y="y",
#     size=10,
#     source=node_source_related_authors,
#     fill_color="steelblue",
#     line_color=None,
# )

# node_renderer_2 = m.scatter(
#     x="x",
#     y="y",
#     size=5,
#     source=node_source_main_authors,
#     fill_color="red",
#     line_color=None,
# )

# m.add_tools(HoverTool(
#     tooltips=[
#         ("Scientist", "@scientist"),
#         ("Works", "@works"),
#         ("Citations", "@citations")
#     ],
#     renderers=[node_renderer_1],
# ))

# show(m)




