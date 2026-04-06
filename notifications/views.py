from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from .models import AppNotification
from .serializers import AppNotificationSerializer


class IsAuthenticated(permissions.IsAuthenticated):
    pass


class AppNotificationViewSet(viewsets.ModelViewSet):
    queryset = AppNotification.objects.all()
    serializer_class = AppNotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['user', 'notification_type', 'is_read']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'detail': 'تم تحديد جميع الإشعارات كمقروءة'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})


router = DefaultRouter()
router.register(r'app-notifications', AppNotificationViewSet, basename='app-notifications')
