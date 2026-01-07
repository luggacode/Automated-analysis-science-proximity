import json

def get_topic_id(input_string):
    """
    Extracts the Topic ID (e.g.,) from a string like:
    'https://openalex.org/T10702'
    """
    # Split on '/' and take the last part
    topic_id = input_string.split("/")[-1]
    return topic_id