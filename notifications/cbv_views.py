"""
Class-Based Views for Notifications App
API using Django REST Framework CBV instead of ViewSet
"""
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import AppNotification
from .serializers import AppNotificationSerializer


class IsAuthenticated(permissions.IsAuthenticated):
    pass


# ============================================================
# AppNotification API (Class-Based Views)
# ============================================================

class AppNotificationListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/notifications/app-notifications/     → List notifications
    POST /api/notifications/app-notifications/     → Create notification
    """
    serializer_class = AppNotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['user', 'notification_type', 'is_read']

    def get_queryset(self):
        return AppNotification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AppNotificationDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/notifications/app-notifications/<id>/  → Retrieve notification
    PUT    /api/notifications/app-notifications/<id>/  → Update notification
    PATCH  /api/notifications/app-notifications/<id>/  → Partial update
    DELETE /api/notifications/app-notifications/<id>/  → Delete notification
    """
    serializer_class = AppNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AppNotification.objects.filter(user=self.request.user)


class AppNotificationMarkAllReadAPIView(APIView):
    """
    POST /api/notifications/app-notifications/mark-all-read/  → Mark all as read
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        AppNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'detail': 'تم تحديد جميع الإشعارات كمقروءة'})


class AppNotificationUnreadCountAPIView(APIView):
    """
    GET /api/notifications/app-notifications/unread-count/  → Unread count
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = AppNotification.objects.filter(user=request.user, is_read=False).count()
        return Response({'count': count})
