import sys
import spacy
import random
import time
import numpy as np
from rake_nltk import Metric, Rake
import re
from spacy.util import minibatch, compounding
from spacy import displacy
import warnings
warnings.filterwarnings("ignore")
nlp = spacy.load('en_core_web_sm')

def NER(test_sentences):
    doc=nlp(test_sentences)
    tokens={}
    genText=test_sentences
    for ent in doc.ents:
        if ent.label_!= 'DATE' and ent.label_!= 'TIME' and ent.label_!= 'MONEY' and ent.label_!= 'QUANTITY' and ent.label_!= 'ORDINAL' and ent.label_!= 'CARDINAL':
            tokens[ent.text]=ent.label_
              
        
    for words in tokens:
        genText=genText.replace(words,'_'+tokens[words]+'_')

    return tokens

    #  #http://127.0.0.1:5000/
    # The above line is for visualising the NER
    #NER("Pranshu is the best. He was born in 1999. Daniel Riccardo is a fool to switch from RedBull Racing to Renault.")

def rake_rank(text):
  r = Rake()
  r.extract_keywords_from_text(text)
  rake_rank=r.get_ranked_phrases()
  no_integers = [x for x in rake_rank if not (x.isdigit() or x[0] == '-' and x[1:].isdigit())]
  return no_integers

def key_search_pair(text):
    rake = rake_rank(text)
    pairs = []
    if len(rake)>=3:
        pairs.append(rake[0] + '+' +  rake[1])
        pairs.append(rake[0] + '+' + rake[2])
        pairs.append(rake[1] + '+' + rake[2])
    elif len(rake)==2:
        pairs.append(rake[0]+ '+' + rake[1])
    else:
        pairs.append(rake[0])
    return (pairs)




