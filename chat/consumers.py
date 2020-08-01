import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        """
        Obtain the room_name parameter from the URL route in chat/routing.py that opened the websocket connection to
        the consumer.
        Each consumer has a scope that contains information about it connection - including positional or keyword
        argument in the URL route and the currently authenticated user if any.
        """
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        # Construct the channel's group name directly from the user specified room name.
        # Group names may contain only letters, digits, hypens and periods, otherwise this code will fail.
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        """
        The async_to_sync wrapper is required because the ChatConsumer is a synchronous WebSocketConsumer but it is 
        calling an asynchronous channel layer method. All channel layer methods are asynchronous.  
        """
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        """
        Accept the WebSocket. If you do not call accept() within the connect() method then the connection will be 
        rejected and closed. You might want to reject a connection for example because the requesting user is not 
        authorized to perform the requested action. It is recommended that accept() be called as the last action in 
        connect() if you choose to accept the connection. 
        """
        self.accept()


    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))