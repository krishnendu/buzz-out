import uuid
from django.shortcuts import get_object_or_404, render
from chat.serializers import UserSerializer, RoomMessagesSerializer, RoomSerializer, MessageSerializer
from chat.models import Room, Message
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from asgiref.sync import async_to_sync

from rest_framework.authtoken.models import Token
from rest_framework import views, response, viewsets, authentication, permissions, status, parsers
from rest_framework.decorators import action

from channels.layers import get_channel_layer

import json

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """

        if self.action in ['register', 'login', 'forget_password']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def user(self, req):
        user = UserSerializer(req.user).data
        return response.Response(user)
    
    @action(detail=False, methods=['get'])
    def filter(self, req):
        queryset = self.get_queryset()
        username = req.query_params.get('username[startswith]')
        if username:
            queryset = queryset.exclude(id=req.user.id).filter(username__istartswith=username)
        users = UserSerializer(queryset, many=True).data
        return response.Response(users)
    
    @action(detail=False, methods=['post'])
    def register(self, req):
        body = req.data
        user_serializer = UserSerializer(data=body)
        if user_serializer.is_valid() :
            user = user_serializer.save()
            return response.Response(user_serializer.data)
        else:
            return response.Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def forget_password(self, req):
        body = req.data
        token = req.query_params.get('token')
        if token:
            cache_key = "forget_password_token_%s" % token
            email = cache.get(cache_key)
            print(email)
            user = None
            if email:
                user = User.objects.filter(email=email).first()
            if not user:
                return response.Response({'error': "User doesn't exist, please regenerate url"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                password = body.get('password')
                if not password:
                    return response.Response({'error': "Password is required"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    user.set_password(password)
                    return response.Response({'success': "Password changed"}, status=status.HTTP_200_OK)
        else:
            user = User.objects.filter(**body).first()
            if not user :
                return response.Response({'error': "User doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if not user.email:
                    return response.Response({'error': "User doesn't have an email"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    token = str(uuid.uuid4())
                    cache_key = "forget_password_token_%s" % token
                    cache.set(cache_key, user.email, 60 * 60 * 2) # 2 hours
                    url = req.META['HTTP_HOST'] + '/api/v1/user/forget_password/?token=%s' % token
                    send_mail(
                        'Buzz-Out Forget password',
                        'You can change the password by clicking the following link: %s\n token : %s' % (url, token),
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=False,
                    )
                    return response.Response({'success': "Mail has been sent"}, status=status.HTTP_200_OK)


    @action(detail=False, methods=['post'])
    def login(self, req):
        body = req.data
        try:
            username = body['username']
        except:
            return response.Response({"error" : "Username required"}, status=404)
        try:
            password = body['password']
        except:
            return response.Response({"error" : "Password required"}, status=404)

        user = authenticate(username=username, password=password)
        user_data = UserSerializer(user).data

        if(not user):
            return response.Response({
                "error" : "Invalid credentials"
            }, status=404)

        token, created = Token.objects.get_or_create(user=user)
        return response.Response({
            'token' : 'Token %s' % token.key,
            'user' : user_data
        })
        
class RoomViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows rooms to be viewed or edited.
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = user.rooms_by_user.all()
        return queryset.order_by('-updated_at')
    
    def create(self, request):
        data = request.data
        data['users'] = data.get('users', list()) + [request.user.id]
        serializer = RoomSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data)
        else:
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        queryset = self.get_queryset()
        return response.Response(RoomMessagesSerializer(queryset, many=True).data)
    
    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        room = get_object_or_404(queryset, pk=pk)
        return response.Response(RoomMessagesSerializer(room).data)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        messages = Message.objects.filter(room_id=pk)
        return response.Response(MessageSerializer(messages, many=True).data)
        

class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows rooms to be viewed or edited.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    # def get_queryset(self):
    #     user = self.request.user
    #     queryset = user.rooms_by_user.all()
    #     return queryset.order_by('-updated_at')

    def create(self, request):

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():

            message = serializer.save()
            room = message.room
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)("chat_%d" % room.id, {
                "type": "chat_message",
                "message": json.dumps(serializer.data),
            })
            users = room.users.all()
            for user in users:
                async_to_sync(channel_layer.group_send)("user_%d" % user.id, {
                    "type": "chat_message",
                    "message": json.dumps(serializer.data),
                })
            
            if room.message_set.all().count() > room.total_chat_limit:
                room.message_set.all().order_by('created_at').first().delete()
            return response.Response(serializer.data)
        else:
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)