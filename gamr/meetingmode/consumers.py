# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import MeetingTranscript

from deepcorrect import DeepCorrect

from lexrank import LexRank
from lexrank.mappings.stopwords import STOPWORDS
from path import Path
from nltk.tokenize import sent_tokenize


import os

# Run the following command in terminal to connect to redis channel
# docker run -p 6379:6379 -d redis:5 

#Initializing DeepCorrect
corrector = DeepCorrect('/home/pranshu/GAMR/gamr/meetingmode/deepcorrect/deeppunct_params_en','/home/pranshu/GAMR/gamr/meetingmode/deepcorrect/deeppunct_checkpoint_google_news')

#Initializing dataset for LexRank
print('loading dataset and initializing...')
documents = []
documents_dir = Path('/home/pranshu/GAMR/gamr/meetingmode/total')

for file_path in documents_dir.files('*.txt'):
    with file_path.open(mode='rt', encoding='latin1') as fp:
        documents.append(fp.readlines())


lxr = LexRank(documents, stopwords=STOPWORDS['en'])
print('dataset load done!')
print('server is running!')

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['meeting_code']
        self.room_group_name = 'meeting_%s' % self.room_name
        f = open('/home/pranshu/GAMR/gamr/meetingmode/transcript.txt', 'a')
        f.truncate(0)
        f.close()

        f = open('/home/pranshu/GAMR/gamr/meetingmode/summary.txt', 'a')
        f.truncate(0)
        f.close()

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def fetch_transcript(self, data):
        return 'fetch'

    async def summarize_transcript(self, data):
        transcript = data['raw-transcript']

        print('DataCorrect begins...')
        corrected_data = corrector.correct(transcript)
        sentence = corrected_data[0]['sequence']
        print(sentence)
        print('DataCorrect Ends!')

        f = open('/home/pranshu/GAMR/gamr/meetingmode/transcript.txt', 'a')
        f.write(sentence + '\n')
        f.close()

        # LexRank Begins
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
        # print(req_sentences)

        final_summary = ''
        for sentence in req_sentences :
            final_summary += sentence

        f = open('/home/pranshu/GAMR/gamr/meetingmode/summary.txt', 'a')
        f.truncate(0)
        f.write(final_summary)
        f.close()

        print("lex rank done")
        #LexRank Ends


        file = open('/home/pranshu/GAMR/gamr/meetingmode/summary.txt', mode="rt", encoding='utf-8')
        summary = file.read()
        # print(summary)
        file.close()
        
        final_summary = '<p>' + summary + '</p>'

        return final_summary


    commands = {
        'fetch_transcript':fetch_transcript,
        'summarize_transcript':summarize_transcript
    }

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        raw_transcript = data['raw-transcript']
        transcript = data['transcript']

        summary = await self.commands[data['command']](self, data)
        # print(summary)
        # print(raw_transcript)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'transcript': transcript,
                'summary':summary
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        transcript = event['transcript']
        summary = event['summary']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'transcript': transcript,
            'summary':summary
        }))