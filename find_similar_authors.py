import json
from bokeh.io import output_notebook, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from pyproj import Proj, transform
import geopandas as gpd
from shapely.geometry import Point
from useful_methods import file_exists
from API_call import get_content_from_request, file_exists, get_works_from_request, extract_openalex_id, get_author_info, get_institution_location
from useful_methods import get_topic_id, all_sublists_descending, get_length_works_file

def get_topics_from_author(author_id):
    topic_list, score_list, works_list = [], [], []
    data = get_content_from_request('https://api.openalex.org/authors/' + author_id)
    topics = data['topics']
    for element in topics:
        topic_list.append(get_topic_id(element['id']))
        score_list.append(element['score'])
        works_list.append(element['count'])
    return topic_list, score_list, works_list

def get_top_n_papers(topic_list, paper_count):
    variations = all_sublists_descending(topic_list)
    length = len(topic_list)
    less_than_n = True
    query = 'https://api.openalex.org/works?filter='
    content = {'results': []}
    for n in range(length):
        search_topics = variations[length-n]
        for variation in search_topics:
            if less_than_n:
                for element in variation:
                    if less_than_n:
                        query += 'topics.id:' + str(element) + ','
                query = query.rstrip(query[-1:]) 
                query += '&per-page=50'
                content = get_works_from_request(query, content)
                if int(len(content['results'])) > paper_count:
                    less_than_n = False
                query = 'https://api.openalex.org/works?filter='
    return content
        

def reduce_paper_list(path, file, new_number):
    new_data = {}
    with open(path + file + ".json", "r", encoding="utf-8") as f:
        new_data['results'] = json.load(f)['results'][:new_number]
    with open(path + file + ".json", "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2)

def get_paper_authors(content):
    """
    Returns a dict of every author who has published with a main author plus the main author him/herself
    """
    related_authors = {}
    for work in content:
        for authorship in work['authorships']:
            if not authorship['author']['id'] in related_authors:
                if not authorship['author']['id'] == None:
                    ID = extract_openalex_id(authorship['author']['id'])
                    related_authors[ID] = authorship['author']
    return related_authors

def prepare_author_infos(author_info_list, outProj, inProj):
    query = ''
    for author in author_info_list:
        author_info_list[author] = get_author_info('https://api.openalex.org/authors/' + author)
        lat, lng = get_institution_location(author)
        author_info_list[author]['lat'] = lat
        author_info_list[author]['lng'] = lng
    # Converting Longitude and Latitude to x,y coordinates.
    for author in author_info_list:
        lng = float(author_info_list[author]['lng'])
        lat = float(author_info_list[author]['lat'])
        author_info_list[author]['coords_lng'], author_info_list[author]['coords_lat'] = transform(outProj, inProj, lng, lat)
    return author_info_list

def generate_similar_authors_map(main_author_ID):
    topics_list, score_list, works_list = get_topics_from_author(main_author_ID)
    paper_list = get_top_n_papers(topics_list, 50)['results'][:50]
    author_info_list = get_paper_authors(paper_list)
    author_info_list = prepare_author_infos(author_info_list, outProj, inProj)

    # Splitting between related authors and main author
    related_authors = {
        k: v for k, v in author_info_list.items()
        if k != main_author_ID
    }
    main_author = {
        k: v for k, v in author_info_list.items()
        if k == main_author_ID
    }

    # Generate Node sources for oth author types
    node_source_related_authors = ColumnDataSource(data=dict(    
        x=[related_authors[author]['coords_lng'] for author in related_authors],
        y=[related_authors[author]['coords_lat'] for author in related_authors],
        scientist = [related_authors[author]['display_name'] for author in related_authors],
        works = [related_authors[author]['works_count'] for author in related_authors],
        citations = [related_authors[author]['cited_by_count'] for author in related_authors]
    ))

    node_source_main_authors = ColumnDataSource(data=dict(    
        x=[main_author[author]['coords_lng'] for author in main_author],
        y=[main_author[author]['coords_lat'] for author in main_author],
        scientist = [main_author[author]['display_name'] for author in main_author],
        works = [main_author[author]['works_count'] for author in main_author],
        citations = [main_author[author]['cited_by_count'] for author in main_author]
    ))

    # Creating Map object.
    m = figure(title='Related Scientists Map ' + 'Maurizio De Pitta', width=1400, # main_author[main_author_ID]['display_name']
            height=700, x_range=(-12000000, 9000000),
            y_range=(-1000000, 7000000),
            x_axis_type='mercator', y_axis_type='mercator',
            )
    m.add_tile("CartoDB Positron", retina=True)

    node_renderer_1 = m.scatter(
        x="x",
        y="y",
        size=10,
        source=node_source_related_authors,
        fill_color="steelblue",
        line_color=None,
    )

    node_renderer_2 = m.scatter(
        x="x",
        y="y",
        size=5,
        source=node_source_main_authors,
        fill_color="red",
        line_color=None,
    )

    m.add_tools(HoverTool(
        tooltips=[
            ("Scientist", "@scientist"),
            ("Works", "@works"),
            ("Citations", "@citations")
        ],
        renderers=[node_renderer_1],
    ))

    show(m)

    return m


map_url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
world = gpd.read_file(map_url)
# Initializing pyproj for Converting from longitude,
# latitude to native map projection x, y coordinates.
outProj = Proj(init='epsg:4326')
inProj = Proj(init='epsg:3857')

# topic_description_url = 'https://api.openalex.org/topics/'
# topic_works_url = 'https://api.openalex.org/works?filter=topics.id:'
# topic_id ='T10702'
main_author_ID = 'A5077227646'

# generate_similar_authors_map(main_author_ID)