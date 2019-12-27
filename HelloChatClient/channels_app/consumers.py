import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from HelloChatClient.core.models.message import Message
from HelloChatClient.core.models.user import User


class ChatConsumer(WebsocketConsumer):

    def init_chat(self, data):
        print(data)
        username = data['username']
        user, created = User.objects.get_or_create(username=username)
        content = {
            'command': 'init_chat'
        }
        if not user:
            content['error'] = f'Unable to get or create User with username: {username}'
            self.send_message(content)
        content['success'] = f"Start chat with username: {username}"
        self.send_message(content)

    def fetch_messages(self, data):
        print(data)
        messages = Message.take_messages(count=50)
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        print(data)
        fromUser = data['from']
        text = data['text']
        user, created = User.objects.get_or_create(username=fromUser)
        message = Message.objects.create(author=user, content=text)
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def connect(self):
        self.room_name = 'room'
        self.room_group_name = 'chat_%s' % self.room_name

        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, {'type': 'chat_message', 'message': message})

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))

    def message_to_json(self, message):
        return {
            'id': str(message.id),
            'author': message.author.username,
            'content': message.content,
            'created_at': str(message.created_at)
        }

    commands = {
        'init_chat': init_chat,
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }