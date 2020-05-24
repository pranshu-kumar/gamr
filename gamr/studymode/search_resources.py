import sys
import wikipedia
from youtube_search import YoutubeSearch
from .keyword_ner_search_query import key_search_pair
import re


try: 
    from googlesearch import search
except ImportError:  
    print("No module named 'google' found") 
   
def google_search(text):
    search_results = [] 
    for j in search(text, tld="co.in", num=30, start = 0, stop = 6, pause=2): 
        search_results.append(j)
    return(search_results)    


######## HOVERING ###########
def wiki_summary(text):
    text = text + ' wikipedia'
    search_results = google_search(text)

    wiki_list = search_results[0].split('/')
    search_query = wiki_list[-1].replace('_', ' ')

    summary = (wikipedia.WikipediaPage(title = search_query).summary)
    return(summary)

##############################################
# def og_site(text):
#     list_words = text.split()
#     if len(list_words)>20:
#         query = ' '.join(list_words[0:20])
#     else:
#         query = ' '.join(list_words)
#     return (query)
###############################################

def final_resources(text):
    pairs = key_search_pair(text)
    websites = []
    for i in range(4):
        websites += google_search(pairs[0])[2*i:2+2*i]
        websites += google_search(pairs[1])[2*i:2+2*i]
        websites += google_search(pairs[2])[2*i:2+2*i]

    websites_new = [] 
    [websites_new.append(x) for x in websites if x not in websites_new] 
    return websites_new[0:6]


