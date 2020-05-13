from lexrank import LexRank
from lexrank.mappings.stopwords import STOPWORDS
from path import Path
from nltk.tokenize import sent_tokenize


# print('loading dataset and initializing............')
# documents = []
# documents_dir = Path('/home/pranshu/GAMR/gamr/meetingmode/total')

# for file_path in documents_dir.files('*.txt'):
#     with file_path.open(mode='rt', encoding='latin1') as fp:
#         documents.append(fp.readlines())


# lxr = LexRank(documents, stopwords=STOPWORDS['en'])
# print('dataset load done................')


def preprocess(filename):
    
    file=open(filename,mode='rt',encoding='utf-8')
    text=file.read()
    file.close()
    lines=sent_tokenize(text)    
    return lines

sentences=preprocess('/home/pranshu/GAMR/gamr/meetingmode/transcript.txt')
scores_cont=lxr.rank_sentences(sentences,threshold=None, fast_power_method=True)
req_sentences=[]
for i in range(len(sentences)):    
    if scores_cont[i]>1:
        req_sentences.append(sentences[i])
print(req_sentences)

final_summary = ''
for sentence in req_sentences :
    final_summary += sentence

f = open('/home/pranshu/GAMR/gamr/meetingmode/summary.txt', 'a')
f.truncate(0)
f.write(final_summary)
f.close()

print("lex rank done")

'''def summary__small_size(text):
    n=len(text)
    if n<=3:
        return n
    elif n<=5:
        return 2
    elif n<=9:
        return 3
    elif n<=12:
        return 4

summary=[]
i=0
if len(sentences)<13:
    summary=lxr.get_summary(sentences,summary_size=summary__small_size(sentences),threshold=None)
else:
    while(i<len(sentences)):
        lines=sentences[i:i+3]
        summary+=lxr.get_summary(lines,summary_size=1,threshold=None)
        i=i+3
print(summary)'''


































