# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import MeetingTranscript

from deepsegment import DeepSegment

# Run the following command in terminal to connect to redis channel
# docker run -p 6379:6379 -d redis:5 



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

    async def fetch_transcript(self, data):
        return 'fetch'

    async def summarize_transcript(self, data):
        return 'summary'


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
        print(summary)
        print(raw_transcript)
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