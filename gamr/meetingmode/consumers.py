# chat/consumers.py

from asgiref.sync import sync_to_async
import json
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import MeetingInfo, Meeting
from django.shortcuts import get_object_or_404

from deepcorrect import DeepCorrect

from lexrank import LexRank
from lexrank.mappings.stopwords import STOPWORDS
from path import Path
from nltk.tokenize import sent_tokenize

from django.contrib.auth import get_user_model
import os

from googletrans import Translator

# Run the following command in terminal to connect to redis channel
# docker run -p 6379:6379 -d redis:5 


User = get_user_model()

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
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    @sync_to_async
    def fetch_meeting_info(self, data):
        
        print('fetching meeting info...')
        meeting = Meeting.objects.get(meeting_code=self.room_name)
        
        try:
            meeting_info = MeetingInfo.objects.get(meeting=meeting)
            transcript = meeting_info.transcript
            summary = meeting_info.summary
            translated_summary = meeting_info.translated_summary
            
            return {
                'transcript':transcript,
                'summary':summary,
                'translated_summary':translated_summary
            }
        except:
            print("Meeting Transcript object not created yet! Creating object")
            
            f = open('/home/pranshu/GAMR/gamr/meetingmode/transcript.txt', 'a')
            f.truncate(0)
            f.close()

            f = open('/home/pranshu/GAMR/gamr/meetingmode/summary.txt','a')
            f.truncate(0)
            f.close()
            
            MeetingInfo.objects.create(meeting=meeting)
            meeting_info = MeetingInfo.objects.get(meeting=meeting)
            transcript = meeting_info.transcript
            summary = meeting_info.summary
            translated_summary = meeting_info.translated_summary
            print(translated_summary)
            return {
                'transcript':transcript,
                'summary':summary,
                'translated_summary':translated_summary
            }
        

    async def summarize_transcript(self):

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
                req_sentences.append(sentences[i]+" ")
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
    
    @sync_to_async
    def save_meeting_info(self, final_transcript, final_summary, final_translated_summary):
        print('Saving Transcript...')

        meeting = Meeting.objects.get(meeting_code = self.room_name)
        meeting_info = MeetingInfo.objects.get(meeting=meeting)
        meeting_info.transcript = final_transcript
        meeting_info.summary = final_summary
        meeting_info.translated_summary = final_translated_summary
        meeting_info.save()

        print('Transcript Saved!')

    
    @sync_to_async
    def translate_summary(self, summary, lang):
        translator = Translator()
        translation = translator.translate(summary, dest=lang)
        return translation.text

    commands = {
        'fetch_meeting_info':fetch_meeting_info,
        'summarize_transcript':summarize_transcript,
        'save_meeting_info':save_meeting_info,
        'translate_summary': translate_summary
    }

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def send_content_data(self, transcript, summary, translated_summary, command):
        await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'transcript': transcript,
                    'summary':summary,
                    'translated_summary':translated_summary,
                    'command':command
                }
            )

    async def addPunct(self,raw_transcript):
        print("DeepCorrect begins...")
        corrected_data = corrector.correct(raw_transcript)
        sentence = corrected_data[0]['sequence']
        print("DeepCorrect ends!")
        return sentence
            

    # Receive message from WebSocket
    async def receive(self, text_data):

        data = json.loads(text_data)

        if data['command'] == 'fetch_meeting_info':
            fetched_data = await self.commands[data['command']](self, data)
            transcript = fetched_data['transcript']
            summary = fetched_data['summary']
            translated_summary = fetched_data['translated_summary']
            if transcript != '': 
                await self.send_content_data(transcript, summary, translated_summary,'fetch')            

        elif data['command'] == 'save_meeting_info':
            final_transcript = data['final_transcript']
            final_summary = data['final_summary']
            final_translated_summary = data['final_translated_summary']
            await self.commands[data['command']](self, final_transcript, final_summary, final_translated_summary)

        elif data['command'] == 'translate_summary':
            summary = data['final_summary']
            lang = data['translate_to']
            translated_summary = await self.translate_summary(summary, lang)

            await self.send_content_data('', '',translated_summary,'translate')

        else :
            raw_transcript = data['raw-transcript']
            sentence = await self.addPunct(raw_transcript)

            f = open('/home/pranshu/GAMR/gamr/meetingmode/transcript.txt', 'a')
            f.write(sentence + '\n')
            f.close()

            message = "<b>@" + data['author'] + ": </b>" + sentence + "\r\n<br />"   

            summary = await self.commands[data['command']](self)
        
            # Send message to room group
            await self.send_content_data(message, summary, '','summarize')

    # Receive message from room group
    async def chat_message(self, event):
        transcript = event['transcript']
        summary = event['summary']
        command = event['command']
        translated_summary = event['translated_summary']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'transcript': transcript,
            'summary':summary,
            'translated_summary':translated_summary,
            'command':command
        }))