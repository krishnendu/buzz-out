from lib2to3.pgen2 import token
from django.db import models
from django.conf import settings
import uuid
import secrets 

# from django.dispatch import receiver
# from django.db.models.signals import post_save
# from rest_framework.authtoken.models import Token

# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=100, default='')
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='rooms_by_admin',
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='rooms_by_user',
    )
    total_chat_limit = models.PositiveSmallIntegerField()
    theme = models.CharField(max_length=100, null=True)
    secret = models.CharField(max_length=512, default=secrets.token_hex)
    extra_fields = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Message(models.Model):

    def user_directory_path(instance, filename):
        extension = ''
        if len(filename.rsplit('.', 1))>1:
            extension = '.' + filename.rsplit('.', 1)[1]
        return 'docs/user_{0}/{1}'.format(instance.sent_by.id, (uuid.uuid3(uuid.NAMESPACE_DNS, filename).hex + extension))

    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    message = models.TextField(null=True, default=None)
    file = models.FileField(upload_to=user_directory_path, default=None, null=True)
    extra_fields = models.TextField(null=True, blank=True)
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='messages_by_user',
        on_delete=models.SET_NULL,
        null=True, default=None
    )
    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='messages_read_by_user',
        default=list
    )
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     self.name


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     if created:
#         Token.objects.create(user=instance)