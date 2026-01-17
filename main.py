# MAIN
import json
from nltk.corpus import stopwords

abstract_list = {}

with open('Code/article_batch_1.json') as f:
    entries = json.load(f)[:3]
    for entry in entries:
        print(entry['bibjson']['subject'][0]['term'])