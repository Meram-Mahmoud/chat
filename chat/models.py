from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class UnreadMessageCount(models.Model):
    user = models.OneToOneField(User, related_name='unread_count', on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
