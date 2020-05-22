# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

from lexrank import LexRank
from lexrank.mappings.stopwords import STOPWORDS
from path import Path
from nltk.tokenize import sent_tokenize, RegexpTokenizer

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


    commands = {
        'process_pasted_text':process_pasted_text,
    }

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        pasted_text = data['pasted_text']

        if data['commands'] == 'process_pasted_text':
            summary,len_text, len_summary = await self.process_pasted_text(pasted_text)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'summary': summary,
                'len_text':len_text,
                'len_summary':len_summary
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        summary = event['summary']
        len_text = event['len_text']
        len_summary = event['len_summary']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'summary': summary,
            'len_text':len_text,
            'len_summary':len_summary
        }))