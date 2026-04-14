"""
URLs for Class-Based Views (CBV) - Notifications App
"""
from django.urls import path

from .cbv_views import (
    AppNotificationListCreateAPIView,
    AppNotificationDetailAPIView,
    AppNotificationMarkAllReadAPIView,
    AppNotificationUnreadCountAPIView,
)

urlpatterns = [
    path('app-notifications/', AppNotificationListCreateAPIView.as_view(), name='appnotification-list'),
    path('app-notifications/mark-all-read/', AppNotificationMarkAllReadAPIView.as_view(), name='appnotification-mark-all-read'),
    path('app-notifications/unread-count/', AppNotificationUnreadCountAPIView.as_view(), name='appnotification-unread-count'),
    path('app-notifications/<int:pk>/', AppNotificationDetailAPIView.as_view(), name='appnotification-detail'),
]
