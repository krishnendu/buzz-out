from django.urls import re_path

from ChatApi import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<user_id>\w+)/$', consumers.UserChatConsumer.as_asgi()),
]