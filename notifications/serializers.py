from rest_framework import serializers

from .models import AppNotification


class AppNotificationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_short_name', read_only=True)

    class Meta:
        model = AppNotification
        fields = '__all__'
