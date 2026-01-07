import json
from API_call import get_content_from_request, file_exists
from useful_methods import get_topic_id



def get_topics_from_author(author_id):
    topic_list, score_list, works_list = [], [], []
    if not file_exists('Authors/', author_id + '.json'):
        get_content_from_request('https://api.openalex.org/authors/' + author_id, 'Authors_' + author_id)
    with open('Authors/' + str(author_id)  + ".json", "r", encoding="utf-8") as f:
        data = json.load(f)
    topics = data['topics']
    for element in topics:
        topic_list.append(get_topic_id(element['id']))
        score_list.append(element['score'])
        works_list.append(element['count'])
    return topic_list, score_list, works_list

    
topic_description_url = 'https://api.openalex.org/topics/'
topic_works_url = 'https://api.openalex.org/works?filter=topics.id:'
topic_id ='T10702'

get_content_from_request(topic_description_url + topic_id, 'Topic_descriptions/Topic' + topic_id)
get_content_from_request(topic_works_url + topic_id, 'Topic_works/Topic' + topic_id)

print(get_topics_from_author('A5063212181'))

