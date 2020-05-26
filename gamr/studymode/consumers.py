# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

from lexrank import LexRank
from lexrank.mappings.stopwords import STOPWORDS
from path import Path
from nltk.tokenize import sent_tokenize, RegexpTokenizer

from .search_resources import final_resources 
from .unfurling import OPG
from .keyword_ner_search_query import NER

# Run the following command in terminal to connect to redis channel
# docker run -p 6379:6379 -d redis:5 

print('loading dataset and initializing...')
documents = []
documents_dir = Path('/home/pranshu/GAMR/gamr/meetingmode/total')

for file_path in documents_dir.files('*.txt'):
    with file_path.open(mode='rt', encoding='latin1') as fp:
        documents.append(fp.readlines())


lxr = LexRank(documents, stopwords=STOPWORDS['en'])
print('dataset load done!')
print('server is running!')

class StudyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['username']
        self.room_group_name = 'study_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def process_pasted_text(self, text):
        
        # LexRank Begins
        def preprocess(text):
            lines=sent_tokenize(text)    
            return lines

        sentences=preprocess(text)
        scores_cont=lxr.rank_sentences(sentences,threshold=None, fast_power_method=True)
        req_sentences=[]
        for i in range(len(sentences)):    
            if scores_cont[i]>1:
                req_sentences.append(sentences[i]+" ")
        # print(req_sentences)

        final_summary = ''
        for sentence in req_sentences :
            final_summary += sentence

        tokenizer = RegexpTokenizer(r'\w+')
        summary_token = tokenizer.tokenize(final_summary)
        len_summary = len(summary_token)
        text_token = tokenizer.tokenize(text)
        len_text = len(text_token)
        return final_summary, len_text, len_summary
        #LexRank Ends

    
    async def add_resources(self, text):
        
        print("fetching resources...")
        resources = final_resources(text)
        print("fetching resources done!")

        print("unfurling...")
        all_resources = []
        for resource in resources:
            resource_dir = OPG(resource)
            if not("url" in resource_dir):
                resource_dir.__setitem__("url", resource)
            all_resources.append(resource_dir)
        print("Unfurling done!")

        print("Spacy starts...")
        tokens = dict(NER(text))
        print("Spacy ends!")
        
        return all_resources, tokens


    commands = {
        'process_pasted_text':process_pasted_text,
        'add_resources':add_resources
    }

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)

        if data['command'] == 'process_pasted_text':
            pasted_text = data['pasted_text']
            summary,len_text, len_summary = await self.process_pasted_text(pasted_text)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'command':'send_summary',
                    'summary': summary,
                    'len_text':len_text,
                    'len_summary':len_summary
                }
            )
        
        elif data['command'] == 'add_resources':
            text = data['pasted_text']
            all_resources, tokens = await self.add_resources(text)
        
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'command':'send_resources',
                    'all_resources': all_resources,
                    'tokens':tokens
                }
            )
        # Send message to room group
      

    # Receive message from room group
    async def chat_message(self, event):
        
        if event['command'] == 'send_summary':
            summary = event['summary']
            len_text = event['len_text']
            len_summary = event['len_summary']

            await self.send(text_data=json.dumps({
                'command':'show_summary',
                'summary': summary,
                'len_text':len_text,
                'len_summary':len_summary
            }))

        elif event['command'] == 'send_resources':
            all_resources = event['all_resources']
            tokens = event['tokens']
            await self.send(text_data=json.dumps({
                'command':'show_resources',
                'all_resources':all_resources,
                'tokens':tokens
            }))
        # Send message to WebSocket
     