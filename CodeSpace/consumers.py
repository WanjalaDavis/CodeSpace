import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"user_{self.user_id}"

        # Add the user to a group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data['action']

        if action == 'call':
            # Send a notification to the called user
            await self.channel_layer.group_send(
                f"user_{data['called_user_id']}",
                {
                    'type': 'call.notification',
                    'caller_id': self.user_id,
                    'caller_name': data['caller_name'],
                }
            )
        elif action == 'accept':
            # Notify the caller that the call was accepted
            await self.channel_layer.group_send(
                f"user_{data['caller_id']}",
                {
                    'type': 'call.accepted',
                }
            )
        elif action == 'reject':
            # Notify the caller that the call was rejected
            await self.channel_layer.group_send(
                f"user_{data['caller_id']}",
                {
                    'type': 'call.rejected',
                }
            )

    # Custom event handlers
    async def call_notification(self, event):
        await self.send(text_data=json.dumps({
            'action': 'notify',
            'caller_id': event['caller_id'],
            'caller_name': event['caller_name'],
        }))

    async def call_accepted(self, event):
        await self.send(text_data=json.dumps({'action': 'accepted'}))

    async def call_rejected(self, event):
        await self.send(text_data=json.dumps({'action': 'rejected'}))
