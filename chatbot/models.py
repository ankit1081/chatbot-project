from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    response = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    session_id = models.CharField(max_length=100)  # Unique identifier for a chat session
    sender = models.CharField(max_length=50)  # 'user' or 'bot'
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.message[:50]}"