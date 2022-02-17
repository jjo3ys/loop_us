from .models import Msg
from rest_framework import serializers

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Msg
        fields = ['id', 'room_id', 'receiver_id', 'message', 'date', 'is_read']