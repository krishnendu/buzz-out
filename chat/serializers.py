from django.contrib.auth.models import User
from chat.models import Room, Message

from rest_framework import serializers
from ChatApi.custom_serializers import JsonListField

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['groups', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'user_permissions']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
        }
    
    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def update(self, instance, validated_data):
        if(validated_data.get('password')):
            instance.set_password(validated_data['password'])
            validated_data.pop('password')
        for field in validated_data.keys():
            if(hasattr(instance, field)):
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance

class RoomSerializer(serializers.ModelSerializer):
    extra_fields = JsonListField(required=False, allow_null=True, default=None)

    class Meta:
        model = Room
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    extra_fields = JsonListField(required=False, allow_null=True, default=None)

    class Meta:
        model = Message
        fields = '__all__'
        extra_kwargs = {
            'read_by': {'required': False, 'allow_empty': True},
        }
    
    # def create(self, validated_data):
    #     user = Message.objects.create(**validated_data)
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     return user

class RoomMessagesSerializer(serializers.ModelSerializer):
    extra_fields = JsonListField(required=False, allow_null=True, default=None)
    message = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = '__all__'

class MessageRoomSerializer(serializers.ModelSerializer):
    extra_fields = JsonListField(required=False, allow_null=True, default=None)
    room = RoomSerializer(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'
