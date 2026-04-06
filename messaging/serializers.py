from rest_framework import serializers

from .models import InternalMessage


class InternalMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_short_name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.get_short_name', read_only=True)

    class Meta:
        model = InternalMessage
        fields = '__all__'
