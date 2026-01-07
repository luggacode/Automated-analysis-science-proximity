import json 
import re
import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from functools import reduce 
from rank_bm25 import BM25Okapi
from tqdm import tqdm
import networkx as nx
import matplotlib.pyplot as plt
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool


relevant_information = {
    'journal': '',
    'publisher':'',
    'language':'',
    'title': '',
    'author': '',
    'abstract':''
}

ps = PorterStemmer()
lemmatizer = WordNetLemmatizer()

class JsonHandler():
    def __init__(self, filepath):
        self.filepath = filepath
        self.content = None

    def get_content(self, relevant_information) -> str:
        abstract_list = {}
        title_list = {}
        authors_list = {}
        with open(self.filepath) as f:
            entries = json.load(f)[:5000]
        for entry in entries:
            if 'bibjson' not in entry:
                continue
            if 'subject' not in entry['bibjson']:
                continue
            if 'abstract' not in entry['bibjson']:
                continue
            if 'title' not in entry['bibjson']:
                continue
            subject_term = entry['bibjson']['subject'][0]['term']
            if subject_term not in abstract_list:
                abstract_list[subject_term] = []
                title_list[subject_term] = []
                # authors_list[subject_term] = []
            abstract_list[subject_term].append(entry['bibjson']['abstract'])
            title_list[subject_term].append(entry['bibjson']['title'])
            # authors_list[subject_term].append(entry['bibjson']['author'])
            for feature in entry['bibjson']:
                # for important_feature in relevant_information:
                for info in relevant_information:
                    if info == feature:
                        relevant_information[info] = entry['bibjson'][feature]
        return abstract_list, title_list
    
def clean_data(abstract_list):
    stopwords_list = ['aim', 'research', 'result', 'shows', 'method', 'novel', 'robust', 'demonstrate', 'report', 'propose', 'effect', 'may', 'year', 'like', 'often', 'however', 'best', 'author', 'problem']
    for subject in abstract_list:
        print('Data cleaning of ' + subject )
        for ind, element in tqdm(enumerate(abstract_list[subject]), total=len(abstract_list[subject])):
            content = element
            content = re.sub('ä', 'ae', content)
            content = re.sub('ö', 'oe', content)
            content = re.sub('ü', 'ue', content)
            content = re.sub("[^A-Za-z0-9]+", " ", content)
            content = content.lower().split()
            content = [word for word in content if not word.isdigit()]
            content = [word for word in content if word not in stopwords_list]
            content = [word for word in content if word not in stopwords.words('english')]
            # content = [lemmatizer.lemmatize(word) for word in content]
            content = [ps.stem(word) for word in content]
            content = [word for word in content if word not in stopwords_list]
            content = ' '.join(content)
            abstract_list[subject][ind] = content
    return abstract_list

def compare_texts(text1, text2):
    comparison_text_1 = text1.split()
    comparison_text_2 = text2.split()
    comparison_text_2 = [word for word in comparison_text_2 if word in comparison_text_1]
    return comparison_text_2



print('Klasse initialisieren')
test = JsonHandler('Code/article_batch_1.json')

print('Abstracts speichern')
abstract_list, title_list = test.get_content(relevant_information)
print('title list medicine')
print(title_list['Medicine'])
print('Data cleaning')
abstract_list = clean_data(abstract_list)

print('Corpus tokenization')
tokenized_corpus = {}
for subject in abstract_list:
    tokenized_corpus[subject] = [doc.split(" ") for doc in abstract_list[subject]] # split every abstract into tokens at every blank space

similarity_scores = {}
for subject in abstract_list:
    similarity_scores[subject] = np.empty([len(abstract_list[subject]), len(abstract_list[subject])])

for subject in abstract_list:
    print('BM25 Okapi calculations ' + subject)
    bm25 = BM25Okapi(tokenized_corpus[subject])
    for ind, abstract in tqdm(enumerate(abstract_list[subject]), total=len(abstract_list[subject])):
        tokenized_query = abstract.split(" ")
        doc_scores = bm25.get_scores(tokenized_query)
        i = 0
        for score in doc_scores:
            similarity_scores[subject][i][ind] = score
            i += 1
for subject in similarity_scores:
    similarity_scores[subject] = similarity_scores[subject] + similarity_scores[subject].T

print('Vergleich Abstract 0 mit den jeweiligen Similarity scores:')

print(abstract_list['Medicine'][0])

for ind, score in enumerate(similarity_scores['Medicine'][0]):
    print('Score im Vergleich mit Abstract' + str(ind) + ': ' + str(score))
    print(abstract_list['Medicine'][ind])
    print('++++++++++++++++++++++++++++')
    print('gleiche Worte:')
    print(compare_texts(abstract_list['Medicine'][0], abstract_list['Medicine'][ind]))
    print('-------------------------------------------------')



# idx = np.argsort(similarity_scores['Medicine'][0,:])

# sorted_arr = similarity_scores['Medicine'][0, idx]
# sorted_texts = [abstract_list['Medicine'][i] for i in idx]
    
# print('SORTED ABSTRACTS')
# for ind, score in enumerate(sorted_arr[(len(abstract_list['Medicine'])-20):]):
#     print('Score im Vergleich mit Abstract ' + str(ind) + ': ' + str(score))
#     print(sorted_texts[ind])
#     print('++++++++++++++++++++++++++++')
#     print('gleiche Worte:')
#     print(compare_texts(abstract_list['Medicine'][0], sorted_texts[ind]))
#     print('------------------------------------')

# G = nx.Graph()
# for ind, number in enumerate(similarity_scores['Medicine']):
#     G.add_node(ind, title = title_list['Medicine'][ind])
# for ind, connections in enumerate(similarity_scores['Medicine']):
#     readout = ind
#     while readout > 0:
#         G.add_edge(ind, readout - 1, weight = connections[readout - 1])
#         readout -= 1

# pos = nx.spring_layout(G)

# node_source = ColumnDataSource(data=dict(
#     x=[pos[n][0] for n in G.nodes()],
#     y=[pos[n][1] for n in G.nodes()],
#     title=[G.nodes[n]["title"] for n in G.nodes()],
#     # author=[G.nodes[n]["author"] for n in G.nodes()],
# ))

# p = figure(
#     tools="pan,wheel_zoom,reset,save",
#     active_scroll="wheel_zoom",
#     width=800,
#     height=600,
# )

# node_renderer = p.circle(
#     x="x",
#     y="y",
#     size=10,
#     source=node_source,
#     fill_color="steelblue",
#     line_color=None,
# )

# p.add_tools(HoverTool(
#     tooltips=[
#         ("Title", "@title"),
#         # ("Author", "@author"),
#     ],
#     renderers=[node_renderer],
# ))

# show(p)

        
# plt.figure(figsize=(6, 6))
# nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=400)

# nx.draw_networkx_labels(
#     G,
#     pos,
#     font_size=12,
#     font_family='sans-serif'
# )

# # Draw the edges
# # nx.draw_networkx(G, pos)

# plt.title("NetworkX Graph with Node and Edge Attributes")
# plt.show()



