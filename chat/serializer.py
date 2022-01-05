from .models import Msg
from rest_framework import serializers

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Msg
        fields = ['sender', 'receiver', 'message', 'date', 'is_read']